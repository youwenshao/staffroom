from flask import Flask, render_template, request, redirect, url_for
import base64
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

# In-memory storage for lesson plans
lesson_plans = []
unit_plans = []

# Allowed file extensions for diagrams
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_file(file_field):
    """Process uploaded file and return base64 encoded string"""
    if file_field not in request.files:
        return None

    file = request.files.get(file_field)
    if file and file.filename and allowed_file(file.filename):
        # Read file and encode as base64
        file_data = file.read()
        encoded_file = base64.b64encode(file_data).decode('utf-8')
        mime_type = file.content_type
        return f"data:{mime_type};base64,{encoded_file}"
    
    return None

@app.context_processor
def inject_feedback_data():
    """Make current URL available to all templates for feedback links"""
    return dict(current_url=request.url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-lesson', methods=['GET'])
def create_plan_form():
    default_values = get_default_values()
    return render_template('create_plan.html', **default_values)

@app.route('/create-unit', methods=['GET'])
def create_unit_form():
    default_values = get_unit_default_values()
    return render_template('create_unit_plan.html', **default_values)

@app.route('/create-lesson', methods=['POST'])
def create_lesson():
    # Extract form data - English fields
    teacher_name = request.form.get('teacher_name')
    pesh_year = request.form.get('pesh_year')
    date = request.form.get('date')
    class_duration = request.form.get('class_duration')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    school_name = request.form.get('school_name')
    year = request.form.get('year')
    class_id = request.form.get('class_id')
    class_level = request.form.get('class_level')
    class_size = request.form.get('class_size')
    boys = request.form.get('boys')
    girls = request.form.get('girls')
    topic = request.form.get('topic')
    unit_duration = request.form.get('unit_duration')
    day_of_unit = request.form.get('day_of_unit')
    lesson_theme = request.form.get('lesson_theme')
    ability_level = request.form.get('ability_level')
    psychomotor_objs = request.form.get('psychomotor_objs')
    cognitive_objs = request.form.get('cognitive_objs')
    affective_objs = request.form.get('affective_objs')
    venue = request.form.get('venue')
    equipment = request.form.get('equipment')
    safety_concerns = request.form.get('safety_concerns')
    
    # Lesson section times and details - English
    intro_time = request.form.get('intro_time')
    intro_cues = request.form.get('intro_cues')
    intro_equipment = request.form.get('intro_equipment')
    
    sd_time = request.form.get('sd_time')
    sd_cues = request.form.get('sd_cues')
    sd_equipment = request.form.get('sd_equipment')
    
    appli_time = request.form.get('appli_time')
    appli_cues = request.form.get('appli_cues')
    appli_equipment = request.form.get('appli_equipment')
    
    ca_time = request.form.get('ca_time')
    ca_cues = request.form.get('ca_cues')
    ca_equipment = request.form.get('ca_equipment')
    
    followup_actions = request.form.get('followup_actions')
    self_reflection = request.form.get('self_reflection')
    
    # Extract Chinese form data
    teacher_name_zh = request.form.get('teacher_name_zh')
    school_name_zh = request.form.get('school_name_zh')
    class_id_zh = request.form.get('class_id_zh')
    class_level_zh = request.form.get('class_level_zh')
    topic_zh = request.form.get('topic_zh')
    lesson_theme_zh = request.form.get('lesson_theme_zh')
    psychomotor_objs_zh = request.form.get('psychomotor_objs_zh')
    cognitive_objs_zh = request.form.get('cognitive_objs_zh')
    affective_objs_zh = request.form.get('affective_objs_zh')
    venue_zh = request.form.get('venue_zh')
    equipment_zh = request.form.get('equipment_zh')
    safety_concerns_zh = request.form.get('safety_concerns_zh')
    intro_cues_zh = request.form.get('intro_cues_zh')
    intro_equipment_zh = request.form.get('intro_equipment_zh')
    sd_cues_zh = request.form.get('sd_cues_zh')
    sd_equipment_zh = request.form.get('sd_equipment_zh')
    appli_cues_zh = request.form.get('appli_cues_zh')
    appli_equipment_zh = request.form.get('appli_equipment_zh')
    ca_cues_zh = request.form.get('ca_cues_zh')
    ca_equipment_zh = request.form.get('ca_equipment_zh')
    followup_actions_zh = request.form.get('followup_actions_zh')
    self_reflection_zh = request.form.get('self_reflection_zh')
    
    # Process uploaded diagram files
    intro_diagram = process_uploaded_file('intro_file')
    sd_diagram = process_uploaded_file('sd_file')
    appli_diagram = process_uploaded_file('appli_file')
    ca_diagram = process_uploaded_file('ca_file')
    
    # Create new plan with all fields
    new_plan = {
        'id': len(lesson_plans) + 1,
        # English fields
        'teacher_name': teacher_name,
        'pesh_year': pesh_year,
        'date': date,
        'class_duration': class_duration,
        'start_time': start_time,
        'end_time': end_time,
        'school_name': school_name,
        'year': year,
        'class_id': class_id,
        'class_level': class_level,
        'class_size': class_size,
        'boys': boys,
        'girls': girls,
        'topic': topic,
        'unit_duration': unit_duration,
        'day_of_unit': day_of_unit,
        'lesson_theme': lesson_theme,
        'ability_level': ability_level,
        'psychomotor_objs': psychomotor_objs,
        'cognitive_objs': cognitive_objs,
        'affective_objs': affective_objs,
        'venue': venue,
        'equipment': equipment,
        'safety_concerns': safety_concerns,
        'intro_time': intro_time,
        'intro_cues': intro_cues,
        'intro_equipment': intro_equipment,
        'intro_diagram': intro_diagram,
        'sd_time': sd_time,
        'sd_cues': sd_cues,
        'sd_equipment': sd_equipment,
        'sd_diagram': sd_diagram,
        'appli_time': appli_time,
        'appli_cues': appli_cues,
        'appli_equipment': appli_equipment,
        'appli_diagram': appli_diagram,
        'ca_time': ca_time,
        'ca_cues': ca_cues,
        'ca_equipment': ca_equipment,
        'ca_diagram': ca_diagram,
        'followup_actions': followup_actions,
        'self_reflection': self_reflection,
        
        # Chinese fields
        'teacher_name_zh': teacher_name_zh,
        'school_name_zh': school_name_zh,
        'class_id_zh': class_id_zh,
        'class_level_zh': class_level_zh,
        'topic_zh': topic_zh,
        'lesson_theme_zh': lesson_theme_zh,
        'psychomotor_objs_zh': psychomotor_objs_zh,
        'cognitive_objs_zh': cognitive_objs_zh,
        'affective_objs_zh': affective_objs_zh,
        'venue_zh': venue_zh,
        'equipment_zh': equipment_zh,
        'safety_concerns_zh': safety_concerns_zh,
        'intro_cues_zh': intro_cues_zh,
        'intro_equipment_zh': intro_equipment_zh,
        'sd_cues_zh': sd_cues_zh,
        'sd_equipment_zh': sd_equipment_zh,
        'appli_cues_zh': appli_cues_zh,
        'appli_equipment_zh': appli_equipment_zh,
        'ca_cues_zh': ca_cues_zh,
        'ca_equipment_zh': ca_equipment_zh,
        'followup_actions_zh': followup_actions_zh,
        'self_reflection_zh': self_reflection_zh
    }
    
    # Store the plan
    lesson_plans.append(new_plan)
    
    # Redirect to view the plan
    return redirect(url_for('view_plan', plan_id=new_plan['id']))

@app.route('/create-unit', methods=['POST'])
def create_unit():
    # Extract unit plan data
    unit_data = {
        'id': len(unit_plans) + 1,
        'unit_topic': request.form.get('unit_topic'),
        'number_of_lessons': request.form.get('number_of_lessons'),
        'period': request.form.get('period'),
        'class_info': request.form.get('class_info'),
        'class_size': request.form.get('class_size'),
        'venue': request.form.get('venue'),
        'equipment': request.form.get('equipment'),
        'unit_overview': request.form.get('unit_overview'),
        'skills_topics': request.form.get('skills_topics'),
        'movement_concepts': request.form.get('movement_concepts'),
        'previous_knowledge': request.form.get('previous_knowledge'),
        'learning_outcomes': request.form.get('learning_outcomes'),
        'assessments': request.form.get('assessments'),
        'psychomotor_obj': request.form.get('psychomotor_obj'),
        'cognitive_obj': request.form.get('cognitive_obj'),
        'affective_obj': request.form.get('affective_obj'),
        'psychomotor_chars': request.form.get('psychomotor_chars'),
        'cognitive_chars': request.form.get('cognitive_chars'),
        'affective_chars': request.form.get('affective_chars'),
        'psychomotor_notes': request.form.get('psychomotor_notes'),
        'cognitive_notes': request.form.get('cognitive_notes'),
        'affective_notes': request.form.get('affective_notes'),
        'individual_differences': request.form.get('individual_differences'),
        'enhancing_motivation': request.form.get('enhancing_motivation'),
        'safety_precautions': request.form.get('safety_precautions'),
        'unit_contents': [],  # This would handle multiple days
        'other_considerations': request.form.get('other_considerations'),
        # Chinese fields
        'unit_topic_zh': request.form.get('unit_topic_zh'),
        # ... add other Chinese fields
    }
    
    unit_plans.append(unit_data)
    return redirect(url_for('view_unit_plan', plan_id=unit_data['id']))

@app.route('/lesson/<int:plan_id>')
def view_lesson_plan(plan_id):
    plan = next((p for p in lesson_plans if p['id'] == plan_id), None)
    if plan is None:
        return "Plan not found!", 404
    return render_template('view_lesson_plan.html', plan=plan)

@app.route('/unit/<int:plan_id>')
def view_unit_plan(plan_id):
    plan = next((p for p in unit_plans if p['id'] == plan_id), None)
    if plan is None:
        return "Plan not found!", 404
    return render_template('view_unit_plan.html', plan=plan)

def get_lesson_default_values():
    """Return default values for the form"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
    
    return {
        # English defaults
        'default_teacher': 'John Smith',
        'default_pesh_year': 2,
        'default_date': tomorrow,
        'default_duration': 40,
        'default_start_time': '09:00',
        'default_end_time': '09:40',
        'default_school': 'CUHK FED School',
        'default_year': 5,
        'default_class': 'A',
        'default_level': 'Primary',
        'default_class_size': 30,
        'default_boys': 15,
        'default_girls': 15,
        'default_topic': 'Basketball Fundamentals',
        'default_unit_duration': 5,
        'default_day': 1,
        'default_theme': 'Basic Dribbling Techniques',
        'default_ability': 50,
        'default_psychomotor': 'Students will be able to perform basic dribbling with 70% accuracy',
        'default_cognitive': 'Students will understand the basic rules of dribbling',
        'default_affective': 'Students will demonstrate cooperation during group activities',
        'default_venue': 'School Sports Hall',
        'default_equipment': 'Basketballs, cones, whistles',
        'default_safety': 'Ensure proper spacing between students',
        'default_intro_time': 5,
        'default_intro_cues': 'Focus on ball control',
        'default_intro_equip': '1 ball per student',
        'default_sd_time': 20,
        'default_sd_cues': 'Keep eyes up while dribbling',
        'default_sd_equip': 'Cones for dribbling course',
        'default_appli_time': 10,
        'default_appli_cues': 'Apply skills in game situation',
        'default_appli_equip': 'Small-sided game equipment',
        'default_ca_time': 5,
        'default_ca_cues': 'Cool down and review key points',
        'default_ca_equip': 'None',
        'default_followup': 'Practice stationary dribbling at home',
        'default_reflection': 'Students responded well to visual demonstrations',
        
        # Chinese defaults
        'default_teacher_zh': '張老師',
        'default_school_zh': '香港中文大學附屬學校',
        'default_class_zh': '甲班',
        'default_level_zh': '小學',
        'default_topic_zh': '籃球基礎',
        'default_theme_zh': '基本運球技巧',
        'default_psychomotor_zh': '學生能夠以70%的準確率完成基本運球',
        'default_cognitive_zh': '學生將理解運球的基本規則',
        'default_affective_zh': '學生在小組活動中展現合作精神',
        'default_venue_zh': '學校體育館',
        'default_equipment_zh': '籃球、雪糕筒、哨子',
        'default_safety_zh': '確保學生之間有適當距離',
        'default_intro_cues_zh': '專注於控球',
        'default_intro_equip_zh': '每位學生一個籃球',
        'default_sd_cues_zh': '運球時保持抬頭',
        'default_sd_equip_zh': '運球路線用的雪糕筒',
        'default_appli_cues_zh': '在比賽情境中應用技能',
        'default_appli_equip_zh': '小型比賽設備',
        'default_ca_cues_zh': '放鬆活動及回顧重點',
        'default_ca_equip_zh': '不需要',
        'default_followup_zh': '在家練習原地運球',
        'default_reflection_zh': '學生對視覺演示反應良好'
    }

def get_unit_default_values():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
    return {
        'default_unit_topic': 'Basketball Fundamentals Unit',
        'default_number_lessons': 5,
        'default_period': f"{tomorrow} to {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}",
        'default_class': '5A',
        'default_class_size': 30,
        'default_venue': 'School Sports Hall',
        'default_equipment': 'Basketballs, cones, whistles, bibs',
        # Add more defaults as needed
    }

if __name__ == '__main__':
    app.run(debug=True)
else:
    application = app
