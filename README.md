# staffroom

**Your tool for creating standardized physical education plans.**

Staffroom is a web-based application designed specifically for students in the Department of Sports Science and Physical Education (SSPE) at The Chinese University of Hong Kong (CUHK). It provides a user-friendly interface for creating, organizing, and printing professional lesson plans and unit plans for physical education teaching.

**Live Website:** https://staffroom-opal.vercel.app

---

## Table of Contents

- [Overview](#overview)
- [Who Can Use This App](#who-can-use-this-app)
- [Features](#features)
- [How to Use the App](#how-to-use-the-app)
  - [Creating a Lesson Plan](#creating-a-lesson-plan)
  - [Creating a Unit Plan](#creating-a-unit-plan)
  - [Using the Diagram Tool](#using-the-diagram-tool)
  - [Viewing and Printing Plans](#viewing-and-printing-plans)
- [Technical Information](#technical-information)
  - [System Requirements](#system-requirements)
  - [Technology Stack](#technology-stack)
  - [Project Structure](#project-structure)
  - [Installation and Setup](#installation-and-setup)
  - [Deployment](#deployment)
- [Important Notes](#important-notes)
- [Support and Feedback](#support-and-feedback)

---

## Overview

Staffroom simplifies the process of creating professional physical education lesson plans and unit plans. The application offers:

- **Standardized Templates**: Pre-formatted templates that follow educational standards
- **Dual Language Support**: Create plans in English or Chinese (中文)
- **Visual Diagram Tool**: Built-in tool for creating class organization diagrams
- **Print-Ready Output**: Generate professional PDF-ready documents for printing
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

---

## Who Can Use This App

This application is designed for:
- **SSPE Students**: Current students in the Department of Sports Science and Physical Education at CUHK
- **Faculty Members**: Instructors who need to review or create teaching plans
- **IT Staff**: Department IT personnel responsible for maintaining and reviewing the application

---

## Features

### 1. **Lesson Plan Creation**
   - Comprehensive lesson planning with all required fields
   - Student ability level tracking (Beginner, Intermediate, Advance percentages)
   - Activity planning with timing, content, teaching cues, and equipment
   - Class organization diagram upload
   - Safety concerns and post-lesson reflection sections

### 2. **Unit Plan Creation**
   - Multi-day unit planning
   - Learning objectives and outcomes
   - Movement concepts and skill progression
   - Assessment strategies
   - Resource references

### 3. **Diagram Tool**
   - Interactive canvas for drawing class organization diagrams
   - Export diagrams as PNG images
   - Easy integration into lesson plans

### 4. **Language Support**
   - Full English interface
   - Full Chinese (中文) interface
   - Language-specific templates and formatting

### 5. **Print Functionality**
   - Print-optimized layouts
   - Clean, professional formatting
   - Page break controls for multi-page plans

---

## How to Use the App

### Accessing the Application

1. Open your web browser (Chrome, Firefox, Safari, or Edge recommended)
2. Navigate to: **https://staffroom-opal.vercel.app**
3. The homepage will display options to create a Unit Plan or Lesson Plan

### Creating a Lesson Plan

1. **Click "New Lesson Plan"** or **"Create Lesson Plan"** button on the homepage

2. **Select Template Language**
   - Choose between **English** or **中文 (Chinese)**
   - This determines the language of all labels and instructions

3. **Fill in Basic Information**
   - Student-Teacher's Name
   - PESH Year
   - Date, Duration, Start Time, End Time
   - School Name, Year, Class, Class Size
   - Unit Topic, Unit Duration, Day of the Unit

4. **Lesson Objectives**
   - Enter what students will be able to achieve by the end of the lesson

5. **Lesson Planning Section**
   - Add activities for:
     - **Introductory Activities**: Warm-up and introduction
     - **Skill Development**: Main teaching activities
     - **Application**: Practice and application of skills
     - **Concluding Activities**: Cool-down and wrap-up
   - For each activity, fill in:
     - **Time (mins)**: Duration of the activity
     - **Teaching content/Activity**: Description of the activity
     - **Teaching Cues/Objectives**: Key teaching points
     - **Equipment**: Required equipment list
     - **Class Organisation Diagram**: Upload or create a diagram
   - Click **"+ Add Row"** to add more activities
   - Use the **trash icon** to remove rows (disabled when only one row remains)

6. **Student Ability Levels**
   - Set percentages for:
     - Beginner students
     - Intermediate students
     - Advanced students
   - These must total 100%

7. **After Lesson Section**
   - **Follow-up Actions**: What to do after the lesson
   - **Self-reflection**: Personal reflection on the lesson

8. **Create the Plan**
   - Click **"Create Lesson Plan"** button
   - Your plan will be displayed with a clean, printable format

9. **Print or Edit**
   - Click **"Print Plan"** to print directly
   - Click **"Back to Edit"** to return to the form

### Creating a Unit Plan

1. **Click "New Unit Plan"** or **"Create Unit Plan"** button on the homepage

2. **Select Template Language** (English or Chinese)

3. **Fill in Unit Information**
   - Unit Topic, Duration, Target Class
   - Learning Focus and Objectives
   - Movement Concepts, Movement Skills, Skill Level

4. **Add Daily Plans**
   - The form starts with 5 days pre-populated
   - For each day, enter:
     - Learning objectives
     - Teaching content
     - Teaching foci
   - Click **"+ Add Day"** to add more days if needed

5. **Assessments**
   - Enter assessment methods (optional)

6. **References**
   - List any textbooks, websites, or resources used
   - Separate fields for English and Chinese references

7. **Create the Unit Plan**
   - Click **"Create Unit Plan"** button
   - View and print your completed unit plan

### Using the Diagram Tool

1. **Access the Diagram Tool**
   - Click **"Create Diagram"** button when uploading a diagram in a lesson plan
   - Or navigate directly to the diagram tool section

2. **Draw Your Diagram**
   - Use your mouse or touchpad to draw on the canvas
   - Draw shapes, lines, and annotations to represent:
     - Student positions
     - Movement paths
     - Equipment placement
     - Playing area layout

3. **Save Your Work**
   - Click **"Download PNG"** to save your diagram
   - **Important**: Always download your diagram before leaving the page
   - Return to your lesson plan and upload the downloaded image

4. **Clear and Restart**
   - Click **"Clear Canvas"** to start over

### Viewing and Printing Plans

1. **After creating a plan**, you'll see a formatted view page

2. **Print Options**:
   - Click **"Print Plan"** button
   - Your browser's print dialog will open
   - Select your printer or "Save as PDF"
   - Adjust print settings as needed

3. **Navigation Options**:
   - **Back to Edit**: Returns to the form (note: current data won't be saved)
   - **Create Another Plan**: Start a new plan
   - **Create Lesson/Unit Plan**: Switch to the other plan type

---

## Technical Information

*This section is intended for IT staff and developers reviewing the codebase.*

### System Requirements

- **Web Browser**: Modern browser supporting HTML5, CSS3, and JavaScript (ES6+)
- **Internet Connection**: Required for accessing the hosted application
- **Display Resolution**: Optimized for screens 1024px and wider; responsive for mobile devices

### Technology Stack

- **Backend Framework**: Flask 2.3.3 (Python web framework)
- **Frontend**:
  - HTML5 with Jinja2 templating
  - Bootstrap 5 (CSS framework for responsive design)
  - Vanilla JavaScript (no external dependencies)
- **Deployment**: Vercel (serverless platform)
- **Python Version**: 3.x (see `runtime.txt` for specific version)
- **Dependencies**: See `requirements.txt`

### Project Structure

```
staffroom/
├── app.py                  # Main Flask application file
├── wsgi.py                 # WSGI entry point for deployment
├── requirements.txt        # Python package dependencies
├── runtime.txt            # Python version specification
├── vercel.json            # Vercel deployment configuration
├── TOS.md                 # Terms of Service document
├── README.md              # This file
└── templates/             # HTML templates (Jinja2)
    ├── base.html          # Base template with navigation and footer
    ├── index.html         # Homepage
    ├── create_lesson_plan.html    # Lesson plan creation form
    ├── view_lesson_plan.html      # Lesson plan output/view
    ├── create_unit_plan.html      # Unit plan creation form
    ├── view_unit_plan.html        # Unit plan output/view
    ├── diagram_tool.html          # Interactive diagram creation tool
    └── tos.html                   # Terms of Service page
```

### Key Application Features (Technical)

- **In-Memory Storage**: Plans are stored temporarily in server memory (not persistent across server restarts)
- **File Upload Handling**: Images are converted to base64 and embedded in HTML
- **Form Validation**: Client-side and server-side validation for required fields
- **Responsive Design**: CSS media queries for mobile/tablet/desktop optimization
- **Print Optimization**: CSS print media queries for clean printed output

### Installation and Setup

*For local development or testing:*

1. **Prerequisites**:
   - Python 3.8 or higher
   - pip (Python package installer)

2. **Clone or Download the Repository**

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   Or using Flask's development server:
   ```bash
   flask run
   ```

5. **Access Locally**:
   - Open browser to `http://localhost:5000` (or the port shown in terminal)

### Deployment

The application is currently deployed on **Vercel**:
- **Platform**: Vercel Serverless Functions
- **Configuration**: See `vercel.json` for routing and build configuration
- **Entry Point**: `app.py` (configured as Python serverless function)
- **Static Assets**: Served via Vercel's static file handling

**Deployment Notes**:
- The application uses in-memory storage, meaning data is not persistent between deployments or server restarts
- File uploads are limited to 2MB maximum
- All plans created are temporary and not saved to a database

### Security Considerations

- **Session Management**: Uses Flask's session handling
- **File Upload Security**: 
  - Restricted file types (PNG, JPG, JPEG, GIF, SVG only)
  - File size limit: 2MB
- **Input Validation**: Form data is validated on both client and server side
- **CORS**: Currently allows requests from the deployed domain
- **Environment Variables**: Never commit `.env` files or sensitive credentials to git
  - All secrets must be stored as environment variables
  - If credentials are accidentally committed, they must be rotated immediately
  - Use `git filter-repo` to remove sensitive data from git history if needed

---

## Important Notes

### Data Storage

### Persistence & roles

- Plans and users are stored in Supabase Postgres. Guests can browse but cannot save or retrieve records.
- Diagram files upload to S3-compatible storage (Supabase storage recommended) and only the public URL is stored in Postgres.
- Student-teachers can share plans with selected professors; professors can see their own plans and any shared student plans; admins can see everything.

**Recommendation for Users**: Download or print plans regularly; storage is best-effort and depends on configured database/bucket availability.

### Browser Compatibility

- ✅ **Chrome/Edge**: Fully supported
- ✅ **Firefox**: Fully supported
- ✅ **Safari**: Fully supported
- ⚠️ **Internet Explorer**: Not supported (use a modern browser)

### File Upload Guidelines

- **Supported Formats**: PNG, JPG, JPEG, GIF, SVG
- **Maximum Size**: 2MB per file
- **Recommendation**: Use PNG format for diagrams for best quality

### Printing Tips

- Use **"Print to PDF"** to save digital copies
- Select **"More settings"** in print dialog to adjust:
  - Margins: Recommended "Minimum" or "None"
  - Background graphics: Enable to print colors and styling
  - Scale: 100% recommended

---

## Database, auth, and storage setup

Configure environment variables (Vercel/locally):

- `SECRET_KEY`
- `DATABASE_URL` (Supabase Postgres URL with `sslmode=require`)
- `STORAGE_BUCKET`, `STORAGE_REGION`, `STORAGE_ENDPOINT`, `STORAGE_PUBLIC_BASE` (optional if endpoint already exposes the bucket), `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`

### Required schema (run once)

```sql
create table users (
  id bigserial primary key,
  username text unique not null,
  password_hash text not null,
  role text not null check (role in ('student-teacher','professor','admin')),
  created_at timestamptz default now()
);

create table professor_student (
  professor_id bigint references users(id) on delete cascade,
  student_id bigint references users(id) on delete cascade,
  primary key (professor_id, student_id)
);

create table lesson_plans (
  id bigserial primary key,
  owner_id bigint references users(id) on delete cascade,
  plan_data jsonb not null,
  shared_professors bigint[] default '{}',
  created_at timestamptz default now()
);
create index lesson_owner_idx on lesson_plans(owner_id);
create index lesson_shared_idx on lesson_plans using gin (shared_professors);

create table unit_plans (
  id bigserial primary key,
  owner_id bigint references users(id) on delete cascade,
  plan_data jsonb not null,
  shared_professors bigint[] default '{}',
  created_at timestamptz default now()
);
create index unit_owner_idx on unit_plans(owner_id);
create index unit_shared_idx on unit_plans using gin (shared_professors);
```

### Role behavior

- `student-teacher`: create/view own plans; pick professors to share; saved to Postgres.
- `professor`: create/view own plans + any student-teacher who shared with them or is mapped in `professor_student`.
- `admin`: full visibility.
- `guest`: browsing only; no saving/retrieval.

---

## Support and Feedback

### For Users (SSPE Students)

If you encounter issues or have questions:
1. Check this README for guidance
2. Contact your course instructor
3. Use the feedback form on the website (if available)

### For IT Staff

**Code Review Information**:
- Templates use Jinja2 syntax for dynamic content.
- Form submissions are handled via POST requests; plan payloads are stored as JSONB in Postgres.
- Client-side JavaScript handles dynamic form features (adding rows, file previews, etc.).
- Storage for diagrams is via S3-compatible buckets; URLs are persisted in Postgres.

**Code Quality Notes**:
- Inline styles and scripts are used in templates for simplicity.
- No build step required; pure Python/Flask backend with psycopg2/bcrypt/boto3.
- Frontend uses vanilla JavaScript (no frameworks).

### Terms of Service

Users should review the Terms of Service available at `/TOS.md` or the Terms of Service page within the application.

---

## Credits

**Developed for**: Department of Sports Science and Physical Education, CUHK  
**Faculty**: CUHK Faculty of Education  
**Copyright**: © 2025 CUHK Department of Sports Science and Physical Education

---

*Last Updated: January 2025*
