from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, abort
import base64
import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from werkzeug.utils import secure_filename

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    import psycopg2
    from psycopg2 import pool, extras
except ImportError:  # pragma: no cover - psycopg2 is required in prod
    psycopg2 = None
    pool = None
    extras = None

import bcrypt
import boto3
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

# Allowed file extensions for diagrams
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

# Database setup (Supabase Postgres via standard connection URL)
# Environment variables are checked at runtime (not module load time) for serverless compatibility

def ensure_ssl_in_connection_string(conn_string):
    """Ensure SSL mode is set in connection string for Supabase."""
    if not conn_string:
        return conn_string
    # If connection string already has parameters, append sslmode
    if '?' in conn_string:
        if 'sslmode=' not in conn_string:
            conn_string += '&sslmode=require'
    else:
        conn_string += '?sslmode=require'
    return conn_string


def get_database_url():
    """
    Get database connection URL from environment variables at runtime.
    Supports multiple variable names used by Vercel Supabase Integration.
    """
    # Check for environment variables in order of preference
    # Vercel Supabase Integration may set any of these
    env_var_names = [
        'DATABASE_URL',
        'POSTGRES_URL',
        'POSTGRES_PRISMA_URL',
        'POSTGRES_URL_NON_POOLING',
        'SUPABASE_DB_URL',
        'SUPABASE_POSTGRES_URL',
    ]
    
    for var_name in env_var_names:
        url = os.environ.get(var_name)
        if url:
            # Log which variable was found (for debugging, but mask sensitive parts)
            masked_url = url.split('@')[-1] if '@' in url else '***'
            print(f"Found database URL from environment variable: {var_name} (host: {masked_url})")
            return ensure_ssl_in_connection_string(url)
    
    # If no variable found, log comprehensive diagnostic information
    # (only log variable names, not values, for security)
    all_env_vars = sorted(list(os.environ.keys()))
    postgres_vars = [v for v in all_env_vars if 'POSTGRES' in v.upper() or 'DATABASE' in v.upper() or 'SUPABASE' in v.upper()]
    
    print(f"No database URL found. Checked: {', '.join(env_var_names)}")
    
    if postgres_vars:
        print(f"Found related environment variables: {', '.join(postgres_vars)}")
    else:
        print("No database-related environment variables found.")
    
    # Log ALL environment variable names for comprehensive debugging
    # This helps identify if Vercel Integration variables exist with unexpected names
    print(f"Total environment variables available: {len(all_env_vars)}")
    if len(all_env_vars) > 0:
        # Show first 20 env var names as a sample (to avoid log spam)
        sample_vars = all_env_vars[:20]
        print(f"Sample environment variables (first 20): {', '.join(sample_vars)}")
        if len(all_env_vars) > 20:
            print(f"... and {len(all_env_vars) - 20} more environment variables")
    
    # Provide helpful message for manual configuration
    print("=" * 80)
    print("DIAGNOSTIC: Database connection string not found in environment variables.")
    print("SOLUTION: Set DATABASE_URL in Vercel Dashboard:")
    print("  1. Go to Vercel Project → Settings → Environment Variables")
    print("  2. Add variable: DATABASE_URL = postgresql://user:pass@host:5432/db?sslmode=require")
    print("  3. Get connection string from Supabase Dashboard → Project Settings → Database")
    print("  4. Ensure variable is set for 'Preview' environment (or all environments)")
    print("  5. Redeploy after adding the variable")
    print("=" * 80)
    
    return None

# Object storage (S3-compatible, e.g., Supabase storage)
STORAGE_BUCKET = os.environ.get('STORAGE_BUCKET')
STORAGE_REGION = os.environ.get('STORAGE_REGION')
STORAGE_ENDPOINT = os.environ.get('STORAGE_ENDPOINT')
STORAGE_PUBLIC_BASE = os.environ.get('STORAGE_PUBLIC_BASE')
STORAGE_ACCESS_KEY = os.environ.get('STORAGE_ACCESS_KEY')
STORAGE_SECRET_KEY = os.environ.get('STORAGE_SECRET_KEY')

STORAGE_ENABLED = all([STORAGE_BUCKET, STORAGE_ACCESS_KEY, STORAGE_SECRET_KEY])
s3_client = None
if STORAGE_ENABLED:
    s3_client = boto3.client(
        "s3",
        endpoint_url=STORAGE_ENDPOINT,
        region_name=STORAGE_REGION,
        aws_access_key_id=STORAGE_ACCESS_KEY,
        aws_secret_access_key=STORAGE_SECRET_KEY,
    )
    if not STORAGE_PUBLIC_BASE:
        base_endpoint = STORAGE_ENDPOINT.rstrip("/") if STORAGE_ENDPOINT else f"https://{STORAGE_BUCKET}.s3.amazonaws.com"
        STORAGE_PUBLIC_BASE = f"{base_endpoint}/{STORAGE_BUCKET}".rstrip("/")


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_object_storage(file_obj):
    """Upload to object storage, return public URL or None."""
    if not STORAGE_ENABLED or not s3_client:
        return None
    key = f"diagrams/{uuid.uuid4()}-{secure_filename(file_obj.filename)}"
    try:
        s3_client.upload_fileobj(
            file_obj,
            STORAGE_BUCKET,
            key,
            ExtraArgs={"ACL": "public-read", "ContentType": file_obj.content_type},
        )
    except (BotoCoreError, ClientError):
        return None
    return f"{STORAGE_PUBLIC_BASE}/{key}"


def process_uploaded_file(file_field):
    """Process uploaded file and return storage URL or base64 fallback."""
    if file_field not in request.files:
        return None

    file = request.files.get(file_field)
    if file and file.filename and allowed_file(file.filename):
        storage_url = upload_to_object_storage(file)
        if storage_url:
            return storage_url
        # Fallback to base64 to preserve behavior when storage is unavailable
        file.seek(0)
        file_data = file.read()
        encoded_file = base64.b64encode(file_data).decode('utf-8')
        mime_type = file.content_type
        return f"data:{mime_type};base64,{encoded_file}"
    return None


def get_db_conn():
    """Create a new database connection. Serverless-friendly (no pooling)."""
    if not psycopg2:
        raise RuntimeError("psycopg2 is not installed. Database functionality is unavailable.")
    
    # Get database URL at runtime (not module load time) for serverless compatibility
    database_url = get_database_url()
    
    if not database_url:
        raise RuntimeError(
            "Database is not configured. Set one of: DATABASE_URL, POSTGRES_URL, POSTGRES_PRISMA_URL, "
            "POSTGRES_URL_NON_POOLING, SUPABASE_DB_URL, or SUPABASE_POSTGRES_URL."
        )
    
    try:
        # Create a new connection for each request (serverless-friendly)
        # SSL is handled via connection string parameters
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        # Log error for debugging in Vercel logs
        print(f"Database connection error: {str(e)}")
        # Mask sensitive connection string in error message
        error_msg = str(e)
        if '@' in error_msg:
            # Mask password in error messages
            parts = error_msg.split('@')
            if len(parts) > 1:
                error_msg = '***@' + '@'.join(parts[1:])
        raise RuntimeError(f"Failed to connect to database: {error_msg}")


@contextmanager
def db_cursor():
    """Context manager for database operations with automatic cleanup."""
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        try:
            yield conn, cur
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Log error for debugging
            print(f"Database operation error: {str(e)}")
            raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"Error closing database connection: {str(e)}")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_user_by_username(username: str):
    """Get user by username. Returns None if not found or on error."""
    try:
        with db_cursor() as (_, cur):
            cur.execute("SELECT id, username, password_hash, role FROM users WHERE username=%s", (username,))
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching user '{username}': {str(e)}")
        return None


def create_user(username: str, password: str, role: str):
    """Create a new user. Raises exception on error."""
    hashed = hash_password(password)
    try:
        with db_cursor() as (_, cur):
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id, username, role",
                (username, hashed, role),
            )
            return cur.fetchone()
    except Exception as e:
        print(f"Error creating user '{username}': {str(e)}")
        raise


def get_professors():
    """Get list of all professors. Returns empty list on error."""
    try:
        with db_cursor() as (_, cur):
            cur.execute("SELECT id, username FROM users WHERE role = 'professor' ORDER BY username")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching professors: {str(e)}")
        return []


def ensure_professor_student_links(student_id: int, professor_ids):
    """Create professor-student links. Silently fails on error."""
    if not professor_ids:
        return
    try:
        with db_cursor() as (_, cur):
            for pid in professor_ids:
                cur.execute(
                    """
                    INSERT INTO professor_student (professor_id, student_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (pid, student_id),
                )
    except Exception as e:
        print(f"Error creating professor-student links: {str(e)}")


def is_professor_for_student(professor_id: int, student_id: int) -> bool:
    """Check if professor is linked to student. Returns False on error."""
    try:
        with db_cursor() as (_, cur):
            cur.execute(
                "SELECT 1 FROM professor_student WHERE professor_id=%s AND student_id=%s LIMIT 1",
                (professor_id, student_id),
            )
            return cur.fetchone() is not None
    except Exception as e:
        print(f"Error checking professor-student link: {str(e)}")
        return False


def get_current_user():
    user = session.get("user")
    return user


def set_current_user(user_dict):
    session["user"] = user_dict


def clear_current_user():
    session.pop("user", None)


def login_required(allow_guest=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for("login", next=request.path, message="Please log in to continue."))
            if user.get("is_guest") and not allow_guest:
                return redirect(url_for("login", next=request.path, message="Guests cannot save or retrieve records."))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def save_plan_record(table_name: str, owner_id: int, plan_data: dict, shared_professors):
    """Save a plan record. Raises exception on error."""
    try:
        with db_cursor() as (_, cur):
            cur.execute(
                f"""
                INSERT INTO {table_name} (owner_id, plan_data, shared_professors)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (owner_id, json.dumps(plan_data), shared_professors or []),
            )
            row = cur.fetchone()
            return row["id"]
    except Exception as e:
        print(f"Error saving plan to {table_name}: {str(e)}")
        raise


def fetch_plan_record(table_name: str, plan_id: int):
    """Fetch a plan record. Returns None if not found or on error."""
    try:
        with db_cursor() as (_, cur):
            cur.execute(
                f"""
                SELECT p.id, p.owner_id, p.plan_data, p.shared_professors, p.created_at, u.username as owner_username
                FROM {table_name} p
                JOIN users u ON p.owner_id = u.id
                WHERE p.id = %s
                """,
                (plan_id,),
            )
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching plan from {table_name} (id={plan_id}): {str(e)}")
        return None


def list_plans_for_user(table_name: str, user):
    """List plans for a user. Returns empty list on error."""
    if not user or user.get("is_guest"):
        return []

    try:
        base_select = f"""
            SELECT p.id,
                   p.created_at,
                   p.owner_id,
                   u.username as owner_username,
                   p.plan_data,
                   p.shared_professors
            FROM {table_name} p
            JOIN users u ON p.owner_id = u.id
        """
        params = []
        where_clause = ""

        if user["role"] == "admin":
            where_clause = ""
        elif user["role"] == "professor":
            where_clause = """
                WHERE p.owner_id = %s
                   OR %s = ANY(p.shared_professors)
            """
            params = [user["id"], user["id"]]
        else:
            where_clause = "WHERE p.owner_id = %s"
            params = [user["id"]]

        with db_cursor() as (_, cur):
            cur.execute(base_select + " " + where_clause + " ORDER BY p.created_at DESC", params)
            rows = cur.fetchall()
            summarized = []
            for row in rows:
                plan_data = row["plan_data"] or {}
                title = plan_data.get("lesson_theme") or plan_data.get("unit_topic") or plan_data.get("topic") or "Untitled"
                summarized.append(
                    {
                        "id": row["id"],
                        "owner_username": row["owner_username"],
                        "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                        "title": title,
                    }
                )
            return summarized
    except Exception as e:
        print(f"Error listing plans from {table_name} for user {user.get('id')}: {str(e)}")
        return []


def can_access_plan(record, user):
    if not record or not user or user.get("is_guest"):
        return False
    if user["role"] == "admin":
        return True
    if record["owner_id"] == user["id"]:
        return True
    if user["role"] == "professor":
        shared_professors = record.get("shared_professors") or []
        if user["id"] in shared_professors:
            return True
        return False
    return False


@app.context_processor
def inject_feedback_data():
    """Make current URL and user available to all templates for feedback links"""
    return dict(current_url=request.url, current_user=get_current_user())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    message = request.args.get("message")
    next_url = request.args.get("next") or request.form.get("next")

    if request.method == "POST":
        mode = request.form.get("mode", "login")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            message = "Username and password are required."
            return render_template("login.html", message=message, next_url=next_url)

        try:
            if mode == "signup":
                role = request.form.get("role", "student-teacher")
                role = role if role in ("student-teacher", "professor", "admin") else "student-teacher"
                existing = get_user_by_username(username)
                if existing:
                    message = "Username already exists."
                else:
                    try:
                        user = create_user(username, password, role)
                        set_current_user({"id": user["id"], "username": user["username"], "role": user["role"], "is_guest": False})
                        return redirect(next_url or url_for("dashboard"))
                    except Exception as e:
                        print(f"Error creating user: {str(e)}")
                        message = "Unable to create account. Please try again later."
            else:
                user = get_user_by_username(username)
                if not user:
                    message = "Invalid credentials."
                elif not verify_password(password, user["password_hash"]):
                    message = "Invalid credentials."
                else:
                    set_current_user({"id": user["id"], "username": user["username"], "role": user["role"], "is_guest": False})
                    return redirect(next_url or url_for("dashboard"))
        except RuntimeError as e:
            # Database connection error
            print(f"Database error during login: {str(e)}")
            message = "Database connection error. Please try again later."
        except Exception as e:
            # Other unexpected errors
            print(f"Unexpected error during login: {str(e)}")
            message = "An error occurred. Please try again later."

    return render_template("login.html", message=message, next_url=next_url)


@app.route("/continue-as-guest", methods=["POST"])
def continue_as_guest():
    set_current_user({"id": None, "username": "guest", "role": "guest", "is_guest": True})
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    clear_current_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required(allow_guest=True)
def dashboard():
    user = get_current_user()
    lesson_rows = list_plans_for_user("lesson_plans", user)
    unit_rows = list_plans_for_user("unit_plans", user)
    return render_template("dashboard.html", lesson_plans=lesson_rows, unit_plans=unit_rows)


@app.route("/create-lesson", methods=["GET"])
@login_required(allow_guest=True)
def create_lesson_form():
    default_values = get_lesson_default_values()
    professors = get_professors()
    return render_template("create_lesson_plan.html", professors=professors, **default_values)


@app.route("/create-unit", methods=["GET"])
@login_required(allow_guest=True)
def create_unit_form():
    default_values = get_unit_default_values()
    professors = get_professors()
    return render_template("create_unit_plan.html", professors=professors, **default_values)


@app.route("/create-lesson", methods=["POST"])
@login_required()
def create_lesson():
    user = get_current_user()
    shared_professors = [int(p) for p in request.form.getlist("shared_professors") if p]

    template_language = request.form.get("template_language", "english")
    teacher_name = request.form.get("teacher_name")
    pesh_year = request.form.get("pesh_year")
    date = request.form.get("date")
    class_duration = request.form.get("class_duration")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    school_name = request.form.get("school_name")
    year = request.form.get("year")
    class_id = request.form.get("class_id")
    class_level = request.form.get("class_level")
    class_size = request.form.get("class_size")
    boys = request.form.get("boys")
    girls = request.form.get("girls")
    topic = request.form.get("topic")
    unit_duration = request.form.get("unit_duration")
    day_of_unit = request.form.get("day_of_unit")
    lesson_theme = request.form.get("lesson_theme")
    ability_level = request.form.get("ability_level")
    beginner_percent = request.form.get("beginner_percent")
    intermediate_percent = request.form.get("intermediate_percent")
    advance_percent = request.form.get("advance_percent")
    psychomotor_objs = request.form.get("psychomotor_objs")
    cognitive_objs = request.form.get("cognitive_objs")
    affective_objs = request.form.get("affective_objs")
    venue = request.form.get("venue")
    equipment = request.form.get("equipment")
    safety_concerns = request.form.get("safety_concerns")

    def get_activity_rows(section, lang=""):
        suffix = "_zh" if lang == "zh" else ""
        rows = []
        idx = 1
        while True:
            time_key = f"{section}_time_{idx}{suffix}"
            if time_key not in request.form:
                break
            row = {
                "time": request.form.get(time_key),
                "content": request.form.get(f"{section}_content_{idx}{suffix}"),
                "cues": request.form.get(f"{section}_cues_{idx}{suffix}"),
                "equipment": request.form.get(f"{section}_equipment_{idx}{suffix}"),
            }
            file_key = f"{section}_file_{idx}{suffix}"
            diagram = process_uploaded_file(file_key)
            if diagram:
                row["diagram"] = diagram
            rows.append(row)
            idx += 1
        return rows

    intro_activities = get_activity_rows("intro", "")
    sd_activities = get_activity_rows("sd", "")
    appli_activities = get_activity_rows("appli", "")
    ca_activities = get_activity_rows("ca", "")

    if not intro_activities:
        intro_activities = [{
            "time": request.form.get("intro_time"),
            "cues": request.form.get("intro_cues"),
            "equipment": request.form.get("intro_equipment"),
            "diagram": process_uploaded_file("intro_file"),
        }]

    followup_actions = request.form.get("followup_actions")
    self_reflection = request.form.get("self_reflection")

    teacher_name_zh = request.form.get("teacher_name_zh")
    pesh_year_zh = request.form.get("pesh_year_zh")
    date_zh = request.form.get("date_zh")
    class_duration_zh = request.form.get("class_duration_zh")
    start_time_zh = request.form.get("start_time_zh")
    end_time_zh = request.form.get("end_time_zh")
    school_name_zh = request.form.get("school_name_zh")
    year_zh = request.form.get("year_zh")
    class_id_zh = request.form.get("class_id_zh")
    class_level_zh = request.form.get("class_level_zh")
    class_size_zh = request.form.get("class_size_zh")
    boys_zh = request.form.get("boys_zh")
    girls_zh = request.form.get("girls_zh")
    unit_duration_zh = request.form.get("unit_duration_zh")
    day_of_unit_zh = request.form.get("day_of_unit_zh")
    topic_zh = request.form.get("topic_zh")
    lesson_theme_zh = request.form.get("lesson_theme_zh")
    ability_level_zh = request.form.get("ability_level_zh")
    beginner_percent_zh = request.form.get("beginner_percent_zh")
    intermediate_percent_zh = request.form.get("intermediate_percent_zh")
    advance_percent_zh = request.form.get("advance_percent_zh")
    psychomotor_objs_zh = request.form.get("psychomotor_objs_zh")
    cognitive_objs_zh = request.form.get("cognitive_objs_zh")
    affective_objs_zh = request.form.get("affective_objs_zh")
    venue_zh = request.form.get("venue_zh")
    equipment_zh = request.form.get("equipment_zh")
    safety_concerns_zh = request.form.get("safety_concerns_zh")
    followup_actions_zh = request.form.get("followup_actions_zh")
    self_reflection_zh = request.form.get("self_reflection_zh")

    intro_activities_zh = get_activity_rows("intro", "zh")
    sd_activities_zh = get_activity_rows("sd", "zh")
    appli_activities_zh = get_activity_rows("appli", "zh")
    ca_activities_zh = get_activity_rows("ca", "zh")

    new_plan = {
        "template_language": template_language,
        "teacher_name": teacher_name,
        "pesh_year": pesh_year,
        "date": date,
        "class_duration": class_duration,
        "start_time": start_time,
        "end_time": end_time,
        "school_name": school_name,
        "year": year,
        "class_id": class_id,
        "class_level": class_level,
        "class_size": class_size,
        "boys": boys,
        "girls": girls,
        "topic": topic,
        "unit_duration": unit_duration,
        "day_of_unit": day_of_unit,
        "lesson_theme": lesson_theme,
        "ability_level": ability_level,
        "beginner_percent": beginner_percent,
        "intermediate_percent": intermediate_percent,
        "advance_percent": advance_percent,
        "psychomotor_objs": psychomotor_objs,
        "cognitive_objs": cognitive_objs,
        "affective_objs": affective_objs,
        "venue": venue,
        "equipment": equipment,
        "safety_concerns": safety_concerns,
        "intro_activities": intro_activities,
        "sd_activities": sd_activities,
        "appli_activities": appli_activities,
        "ca_activities": ca_activities,
        "followup_actions": followup_actions,
        "self_reflection": self_reflection,
        "teacher_name_zh": teacher_name_zh,
        "pesh_year_zh": pesh_year_zh,
        "date_zh": date_zh,
        "class_duration_zh": class_duration_zh,
        "start_time_zh": start_time_zh,
        "end_time_zh": end_time_zh,
        "school_name_zh": school_name_zh,
        "year_zh": year_zh,
        "class_id_zh": class_id_zh,
        "class_level_zh": class_level_zh,
        "class_size_zh": class_size_zh,
        "boys_zh": boys_zh,
        "girls_zh": girls_zh,
        "unit_duration_zh": unit_duration_zh,
        "day_of_unit_zh": day_of_unit_zh,
        "topic_zh": topic_zh,
        "lesson_theme_zh": lesson_theme_zh,
        "ability_level_zh": ability_level_zh,
        "beginner_percent_zh": beginner_percent_zh,
        "intermediate_percent_zh": intermediate_percent_zh,
        "advance_percent_zh": advance_percent_zh,
        "psychomotor_objs_zh": psychomotor_objs_zh,
        "cognitive_objs_zh": cognitive_objs_zh,
        "affective_objs_zh": affective_objs_zh,
        "venue_zh": venue_zh,
        "equipment_zh": equipment_zh,
        "safety_concerns_zh": safety_concerns_zh,
        "intro_activities_zh": intro_activities_zh,
        "sd_activities_zh": sd_activities_zh,
        "appli_activities_zh": appli_activities_zh,
        "ca_activities_zh": ca_activities_zh,
        "followup_actions_zh": followup_actions_zh,
        "self_reflection_zh": self_reflection_zh,
    }

    try:
        plan_id = save_plan_record("lesson_plans", user["id"], new_plan, shared_professors)
        if user["role"] == "student-teacher":
            ensure_professor_student_links(user["id"], shared_professors)
        return redirect(url_for("view_lesson_plan", plan_id=plan_id))
    except Exception as e:
        print(f"Error saving lesson plan: {str(e)}")
        flash("Failed to save lesson plan. Please try again.", "error")
        return redirect(url_for("create_lesson_form"))


@app.route("/create-unit", methods=["POST"])
@login_required()
def create_unit():
    user = get_current_user()
    shared_professors = [int(p) for p in request.form.getlist("shared_professors") if p]

    template_language = request.form.get("template_language", "english")
    unit_data = {
        "template_language": template_language,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unit_topic": request.form.get("unit_topic"),
        "number_of_lessons": request.form.get("number_of_lessons"),
        "period": request.form.get("period"),
        "class_info": request.form.get("class_info"),
        "class_level": request.form.get("class_level"),
        "class_size": request.form.get("class_size"),
        "boys": request.form.get("boys"),
        "girls": request.form.get("girls"),
        "venue": request.form.get("venue"),
        "equipment": request.form.get("equipment"),
        "unit_overview": request.form.get("unit_overview"),
        "skills_topics": request.form.get("skills_topics"),
        "movement_concepts": request.form.get("movement_concepts"),
        "previous_knowledge": request.form.get("previous_knowledge"),
        "learning_outcomes": request.form.get("learning_outcomes"),
        "assessments": request.form.get("assessments"),
        "psychomotor_obj": request.form.get("psychomotor_obj"),
        "cognitive_obj": request.form.get("cognitive_obj"),
        "affective_obj": request.form.get("affective_obj"),
        "psychomotor_chars": request.form.get("psychomotor_chars"),
        "cognitive_chars": request.form.get("cognitive_chars"),
        "affective_chars": request.form.get("affective_chars"),
        "psychomotor_notes": request.form.get("psychomotor_notes"),
        "cognitive_notes": request.form.get("cognitive_notes"),
        "affective_notes": request.form.get("affective_notes"),
        "individual_differences": request.form.get("individual_differences"),
        "enhancing_motivation": request.form.get("enhancing_motivation"),
        "safety_precautions": request.form.get("safety_precautions"),
        "other_considerations": request.form.get("other_considerations"),
        "references": request.form.get("references"),
        "unit_contents": [],
    }

    day_num = 1
    while True:
        date_key = f"day_{day_num}_date"
        if date_key not in request.form:
            break
        day_data = {
            "day": day_num,
            "date": request.form.get(date_key),
            "theme": request.form.get(f"day_{day_num}_theme"),
            "activities": request.form.get(f"day_{day_num}_activities"),
        }
        unit_data["unit_contents"].append(day_data)
        day_num += 1

    unit_data.update(
        {
            "unit_topic_zh": request.form.get("unit_topic_zh"),
            "number_of_lessons_zh": request.form.get("number_of_lessons_zh"),
            "period_zh": request.form.get("period_zh"),
            "class_info_zh": request.form.get("class_info_zh"),
            "class_level_zh": request.form.get("class_level_zh"),
            "class_size_zh": request.form.get("class_size_zh"),
            "boys_zh": request.form.get("boys_zh"),
            "girls_zh": request.form.get("girls_zh"),
            "venue_zh": request.form.get("venue_zh"),
            "equipment_zh": request.form.get("equipment_zh"),
            "unit_overview_zh": request.form.get("unit_overview_zh"),
            "skills_topics_zh": request.form.get("skills_topics_zh"),
            "movement_concepts_zh": request.form.get("movement_concepts_zh"),
            "previous_knowledge_zh": request.form.get("previous_knowledge_zh"),
            "learning_outcomes_zh": request.form.get("learning_outcomes_zh"),
            "assessments_zh": request.form.get("assessments_zh"),
            "psychomotor_obj_zh": request.form.get("psychomotor_obj_zh"),
            "cognitive_obj_zh": request.form.get("cognitive_obj_zh"),
            "affective_obj_zh": request.form.get("affective_obj_zh"),
            "psychomotor_chars_zh": request.form.get("psychomotor_chars_zh"),
            "cognitive_chars_zh": request.form.get("cognitive_chars_zh"),
            "affective_chars_zh": request.form.get("affective_chars_zh"),
            "psychomotor_notes_zh": request.form.get("psychomotor_notes_zh"),
            "cognitive_notes_zh": request.form.get("cognitive_notes_zh"),
            "affective_notes_zh": request.form.get("affective_notes_zh"),
            "individual_differences_zh": request.form.get("individual_differences_zh"),
            "enhancing_motivation_zh": request.form.get("enhancing_motivation_zh"),
            "safety_precautions_zh": request.form.get("safety_precautions_zh"),
            "other_considerations_zh": request.form.get("other_considerations_zh"),
            "references_zh": request.form.get("references_zh"),
        }
    )

    unit_data["unit_contents_zh"] = []
    day_num = 1
    while True:
        date_key = f"day_{day_num}_date_zh"
        if date_key not in request.form:
            break
        day_data_zh = {
            "day": day_num,
            "date": request.form.get(date_key),
            "theme": request.form.get(f"day_{day_num}_theme_zh"),
            "activities": request.form.get(f"day_{day_num}_activities_zh"),
        }
        unit_data["unit_contents_zh"].append(day_data_zh)
        day_num += 1

    try:
        plan_id = save_plan_record("unit_plans", user["id"], unit_data, shared_professors)
        if user["role"] == "student-teacher":
            ensure_professor_student_links(user["id"], shared_professors)
        return redirect(url_for("view_unit_plan", plan_id=plan_id))
    except Exception as e:
        print(f"Error saving unit plan: {str(e)}")
        flash("Failed to save unit plan. Please try again.", "error")
        return redirect(url_for("create_unit_form"))


@app.route("/lesson/<int:plan_id>")
@login_required()
def view_lesson_plan(plan_id):
    user = get_current_user()
    try:
        record = fetch_plan_record("lesson_plans", plan_id)
        if not record:
            flash("Lesson plan not found.", "error")
            return redirect(url_for("dashboard"))
        if not can_access_plan(record, user):
            abort(403)
        plan_payload = dict(record["plan_data"] or {})
        plan_payload["id"] = record["id"]
        return render_template("view_lesson_plan.html", plan=plan_payload)
    except Exception as e:
        print(f"Error viewing lesson plan {plan_id}: {str(e)}")
        flash("Error loading lesson plan. Please try again.", "error")
        return redirect(url_for("dashboard"))


@app.route("/unit/<int:plan_id>")
@login_required()
def view_unit_plan(plan_id):
    user = get_current_user()
    try:
        record = fetch_plan_record("unit_plans", plan_id)
        if not record:
            flash("Unit plan not found.", "error")
            return redirect(url_for("dashboard"))
        if not can_access_plan(record, user):
            abort(403)
        plan_payload = dict(record["plan_data"] or {})
        plan_payload["id"] = record["id"]
        return render_template("view_unit_plan.html", plan=plan_payload)
    except Exception as e:
        print(f"Error viewing unit plan {plan_id}: {str(e)}")
        flash("Error loading unit plan. Please try again.", "error")
        return redirect(url_for("dashboard"))


@app.route("/diagram-tool")
def diagram_tool():
    return render_template("diagram_tool.html")


@app.route("/TOS.md")
def tos():
    """Serve the Terms of Service document"""
    tos_path = os.path.join(os.path.dirname(__file__), "TOS.md")
    if os.path.exists(tos_path):
        with open(tos_path, "r", encoding="utf-8") as f:
            tos_content = f.read()

        if MARKDOWN_AVAILABLE:
            html_content = markdown.markdown(tos_content, extensions=["extra", "nl2br"])
        else:
            html_content = "<pre>" + tos_content + "</pre>"

        return render_template("tos.html", tos_content=html_content)
    return "Terms of Service not found", 404


def get_lesson_default_values():
    """Return default values for the form"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    return {
        "default_teacher": "John Smith",
        "default_pesh_year": 2,
        "default_date": tomorrow,
        "default_duration": 40,
        "default_start_time": "09:00",
        "default_end_time": "09:40",
        "default_school": "CUHK FED School",
        "default_year": 5,
        "default_class": "A",
        "default_level": "Primary",
        "default_class_size": 30,
        "default_boys": 15,
        "default_girls": 15,
        "default_topic": "Basketball Fundamentals",
        "default_unit_duration": 5,
        "default_day": 1,
        "default_theme": "Basic Dribbling Techniques",
        "default_ability": 50,
        "default_psychomotor": "Students will be able to perform basic dribbling with 70% accuracy",
        "default_cognitive": "Students will understand the basic rules of dribbling",
        "default_affective": "Students will demonstrate cooperation during group activities",
        "default_venue": "School Sports Hall",
        "default_equipment": "Basketballs, cones, whistles",
        "default_safety": "Ensure proper spacing between students",
        "default_intro_time": 5,
        "default_intro_cues": "Focus on ball control",
        "default_intro_equip": "1 ball per student",
        "default_sd_time": 20,
        "default_sd_cues": "Keep eyes up while dribbling",
        "default_sd_equip": "Cones for dribbling course",
        "default_appli_time": 10,
        "default_appli_cues": "Apply skills in game situation",
        "default_appli_equip": "Small-sided game equipment",
        "default_ca_time": 5,
        "default_ca_cues": "Cool down and review key points",
        "default_ca_equip": "None",
        "default_followup": "Practice stationary dribbling at home",
        "default_reflection": "Students responded well to visual demonstrations",
        "default_teacher_zh": "張老師",
        "default_school_zh": "香港中文大學附屬學校",
        "default_class_zh": "甲班",
        "default_level_zh": "小學",
        "default_topic_zh": "籃球基礎",
        "default_theme_zh": "基本運球技巧",
        "default_psychomotor_zh": "學生能夠以70%的準確率完成基本運球",
        "default_cognitive_zh": "學生將理解運球的基本規則",
        "default_affective_zh": "學生在小組活動中展現合作精神",
        "default_venue_zh": "學校體育館",
        "default_equipment_zh": "籃球、雪糕筒、哨子",
        "default_safety_zh": "確保學生之間有適當距離",
        "default_intro_cues_zh": "專注於控球",
        "default_intro_equip_zh": "每位學生一個籃球",
        "default_sd_cues_zh": "運球時保持抬頭",
        "default_sd_equip_zh": "運球路線用的雪糕筒",
        "default_appli_cues_zh": "在比賽情境中應用技能",
        "default_appli_equip_zh": "小型比賽設備",
        "default_ca_cues_zh": "放鬆活動及回顧重點",
        "default_ca_equip_zh": "不需要",
        "default_followup_zh": "在家練習原地運球",
        "default_reflection_zh": "學生對視覺演示反應良好",
    }


def get_unit_default_values():
    """Return default values for unit plan form"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")

    return {
        "default_unit_topic": "Basketball Fundamentals Unit",
        "default_number_lessons": 5,
        "default_period": f"{tomorrow} to {end_date}",
        "default_class": "5A",
        "default_class_size": 30,
        "default_boys": 15,
        "default_girls": 15,
        "default_venue": "School Sports Hall",
        "default_equipment": "Basketballs, cones, whistles, bibs",
        "default_unit_topic_zh": "籃球基礎單元",
        "default_period_zh": f"{tomorrow} 至 {end_date}",
        "default_class_zh": "五甲班",
        "default_venue_zh": "學校體育館",
        "default_equipment_zh": "籃球、雪糕筒、哨子、號碼衣",
    }


if __name__ == "__main__":
    app.run(debug=True)
else:
    application = app
