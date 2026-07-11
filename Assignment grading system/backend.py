# ==========================================================
# AI ACADEMIC EVALUATION SYSTEM
# BACKEND.PY V3
# SECTION 1
# IMPORTS + GEMINI + DATABASE + TABLES
# ==========================================================

import os
import json
import sqlite3
import bcrypt
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai

from PyPDF2 import PdfReader
from docx import Document


# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )
else:
    model = None


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

conn = sqlite3.connect(
    "lms.db",
    check_same_thread=False
)

cursor = conn.cursor()


# ==========================================================
# USERS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    matric TEXT,
    dept TEXT,
    faculty TEXT,
    created_at TEXT
)
""")


# ==========================================================
# COURSES TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    title TEXT,
    dept TEXT,
    level TEXT,
    lecturer_id INTEGER,
    created_at TEXT
)
""")


# ==========================================================
# ENROLLMENTS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER
)
""")


# ==========================================================
# ASSIGNMENTS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    instructions TEXT,
    rubric TEXT,
    deadline TEXT,
    total_score INTEGER,
    status TEXT,
    created_by INTEGER,
    created_at TEXT
)
""")


# ==========================================================
# SUBMISSIONS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS submissions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    student_id INTEGER,
    file_path TEXT,
    extracted_text TEXT,
    score REAL,
    feedback TEXT,
    ai_raw TEXT,
    status TEXT,
    submitted_at TEXT
)
""")


# ==========================================================
# COMMENTS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    submission_id INTEGER,
    author_id INTEGER,
    message TEXT,
    created_at TEXT
)
""")


# ==========================================================
# ANALYTICS TABLE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS analytics_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    timestamp TEXT
)
""")


conn.commit()

print("✅ Backend Section 1 Loaded")

# ==========================================================
# SECTION 2
# AUTHENTICATION + USERS + COURSES + ENROLLMENTS
# ==========================================================


# ==========================================================
# PASSWORD HASHING
# ==========================================================

def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ==========================================================
# USER REGISTRATION
# ==========================================================

def register_user(
    username,
    password,
    role,
    matric="",
    dept="",
    faculty=""
):

    try:

        hashed_password = hash_password(
            password
        )

        cursor.execute(
            """
            INSERT INTO users(
                username,
                password,
                role,
                matric,
                dept,
                faculty,
                created_at
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                username,
                hashed_password,
                role,
                matric,
                dept,
                faculty,
                datetime.now().isoformat()
            )
        )

        conn.commit()

        return True

    except Exception as e:

        print(
            "Register Error:",
            e
        )

        return False


# ==========================================================
# LOGIN
# ==========================================================

def login_user(
    username,
    password
):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        return None

    stored_password = user[2]

    if verify_password(
        password,
        stored_password
    ):
        return user

    return None


# ==========================================================
# GET USER
# ==========================================================

def get_user(username):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    return cursor.fetchone()


# ==========================================================
# GET USER BY ID
# ==========================================================

def get_user_by_id(user_id):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    return cursor.fetchone()


# ==========================================================
# COURSE FUNCTIONS
# ==========================================================

def add_course(
    course_code,
    title,
    dept,
    level,
    lecturer_id
):

    cursor.execute(
        """
        INSERT INTO courses(
            course_code,
            title,
            dept,
            level,
            lecturer_id,
            created_at
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            course_code,
            title,
            dept,
            level,
            lecturer_id,
            datetime.now().isoformat()
        )
    )

    conn.commit()


def assign_lecturer(
    course_id,
    lecturer_id
):

    cursor.execute(
        """
        UPDATE courses
        SET lecturer_id=?
        WHERE id=?
        """,
        (
            lecturer_id,
            course_id
        )
    )

    conn.commit()


def get_all_courses():

    query = """
    SELECT *
    FROM courses
    ORDER BY created_at DESC
    """

    return pd.read_sql_query(
        query,
        conn
    )


def get_course(course_id):

    cursor.execute(
        """
        SELECT *
        FROM courses
        WHERE id=?
        """,
        (course_id,)
    )

    return cursor.fetchone()


# ==========================================================
# ENROLLMENT FUNCTIONS
# ==========================================================

def enroll_student(
    student_id,
    course_id
):

    cursor.execute(
        """
        INSERT INTO enrollments(
            student_id,
            course_id
        )
        VALUES(?,?)
        """,
        (
            student_id,
            course_id
        )
    )

    conn.commit()


def get_student_courses(
    student_id
):

    query = """
    SELECT
        c.*
    FROM courses c
    JOIN enrollments e
    ON c.id = e.course_id
    WHERE e.student_id=?
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(student_id,)
    )


def get_course_students(
    course_id
):

    query = """
    SELECT
        u.*
    FROM users u
    JOIN enrollments e
    ON u.id = e.student_id
    WHERE e.course_id=?
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(course_id,)
    )


print("✅ Backend Section 2 Loaded")

# ==========================================================
# SECTION 3
# FILE EXTRACTION + AI GRADING + ASSIGNMENTS + SUBMISSIONS
# ==========================================================


# ==========================================================
# PDF EXTRACTION
# ==========================================================

def extract_pdf_text(file_path):

    text = ""

    try:

        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:

        print(
            "PDF Extraction Error:",
            e
        )

    return text


# ==========================================================
# DOCX EXTRACTION
# ==========================================================

def extract_docx_text(file_path):

    text = ""

    try:

        document = Document(file_path)

        text = "\n".join(
            [p.text for p in document.paragraphs]
        )

    except Exception as e:

        print(
            "DOCX Extraction Error:",
            e
        )

    return text


# ==========================================================
# UNIVERSAL TEXT EXTRACTION
# ==========================================================

def extract_text(file_path):

    extension = (
        file_path.split(".")[-1]
        .lower()
    )

    if extension == "pdf":
        return extract_pdf_text(file_path)

    if extension == "docx":
        return extract_docx_text(file_path)

    return ""


# ==========================================================
# GEMINI AI GRADING
# ==========================================================

def grade_with_ai(
    course,
    rubric,
    student_answer
):

    if model is None:

        return {
            "score": 0,
            "feedback": "Gemini API key not configured.",
            "analysis": "Configuration Error"
        }

    prompt = f"""
You are a strict university lecturer.

Course:
{course}

Rubric:
{rubric}

Student Answer:
{student_answer}

Evaluate the answer carefully.

Return ONLY valid JSON:

{{
    "score": 0,
    "feedback": "",
    "analysis": ""
}}
"""

    try:

        response = model.generate_content(
            prompt
        )

        text = response.text.strip()

        text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(text)

    except Exception as e:

        return {
            "score": 0,
            "feedback": str(e),
            "analysis": "AI Processing Error"
        }


# ==========================================================
# ASSIGNMENT FUNCTIONS
# ==========================================================

def create_assignment(
    course_id,
    title,
    instructions,
    rubric,
    deadline,
    total_score,
    lecturer_id
):

    cursor.execute(
        """
        INSERT INTO assignments(
            course_id,
            title,
            instructions,
            rubric,
            deadline,
            total_score,
            status,
            created_by,
            created_at
        )
        VALUES(
            ?,?,?,?,?,?,?,?,?
        )
        """,
        (
            course_id,
            title,
            instructions,
            rubric,
            deadline,
            total_score,
            "open",
            lecturer_id,
            datetime.now().isoformat()
        )
    )

    conn.commit()


def get_course_assignments(
    course_id
):

    query = """
    SELECT *
    FROM assignments
    WHERE course_id=?
    ORDER BY created_at DESC
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(course_id,)
    )


def delete_assignment(
    assignment_id
):

    cursor.execute(
        """
        DELETE FROM assignments
        WHERE id=?
        """,
        (assignment_id,)
    )

    conn.commit()


# ==========================================================
# SUBMISSION FUNCTIONS
# ==========================================================

def submit_assignment(
    assignment_id,
    student_id,
    file_path
):

    extracted_text = extract_text(
        file_path
    )

    cursor.execute(
        """
        INSERT INTO submissions(
            assignment_id,
            student_id,
            file_path,
            extracted_text,
            score,
            feedback,
            ai_raw,
            status,
            submitted_at
        )
        VALUES(
            ?,?,
            ?,?,
            0,
            '',
            '',
            'pending',
            ?
        )
        """,
        (
            assignment_id,
            student_id,
            file_path,
            extracted_text,
            datetime.now().isoformat()
        )
    )

    conn.commit()


def get_submissions(
    assignment_id
):

    query = """
    SELECT *
    FROM submissions
    WHERE assignment_id=?
    ORDER BY submitted_at DESC
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(assignment_id,)
    )


def get_submission(
    submission_id
):

    cursor.execute(
        """
        SELECT *
        FROM submissions
        WHERE id=?
        """,
        (submission_id,)
    )

    return cursor.fetchone()


def get_student_submissions(
    student_id
):

    query = """
    SELECT *
    FROM submissions
    WHERE student_id=?
    ORDER BY submitted_at DESC
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(student_id,)
    )


# ==========================================================
# AI GRADE SUBMISSION
# ==========================================================

def grade_submission(
    submission_id,
    course,
    rubric
):

    submission = get_submission(
        submission_id
    )

    if submission is None:
        return None

    extracted_text = submission[4]

    result = grade_with_ai(
        course,
        rubric,
        extracted_text
    )

    cursor.execute(
        """
        UPDATE submissions
        SET
            score=?,
            feedback=?,
            ai_raw=?,
            status='graded'
        WHERE id=?
        """,
        (
            result["score"],
            result["feedback"],
            json.dumps(result),
            submission_id
        )
    )

    conn.commit()

    return result


def override_grade(
    submission_id,
    score,
    feedback
):

    cursor.execute(
        """
        UPDATE submissions
        SET
            score=?,
            feedback=?,
            status='graded'
        WHERE id=?
        """,
        (
            score,
            feedback,
            submission_id
        )
    )

    conn.commit()


print("✅ Backend Section 3 Loaded")

# ==========================================================
# SECTION 4
# COMMENTS + ANALYTICS + EXPORTS + DEFAULT ADMIN
# ==========================================================


# ==========================================================
# COMMENTS
# ==========================================================

def add_comment(
    assignment_id,
    submission_id,
    author_id,
    message
):

    cursor.execute(
        """
        INSERT INTO comments(
            assignment_id,
            submission_id,
            author_id,
            message,
            created_at
        )
        VALUES(?,?,?,?,?)
        """,
        (
            assignment_id,
            submission_id,
            author_id,
            message,
            datetime.now().isoformat()
        )
    )

    conn.commit()


def get_comments(
    submission_id
):

    query = """
    SELECT *
    FROM comments
    WHERE submission_id=?
    ORDER BY created_at DESC
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(submission_id,)
    )


# ==========================================================
# ACTIVITY LOGS
# ==========================================================

def log_activity(
    user_id,
    action
):

    cursor.execute(
        """
        INSERT INTO analytics_logs(
            user_id,
            action,
            timestamp
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            action,
            datetime.now().isoformat()
        )
    )

    conn.commit()


# ==========================================================
# ADMIN ANALYTICS
# ==========================================================

def get_admin_stats():

    stats = {}

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )
    stats["total_users"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM courses"
    )
    stats["total_courses"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assignments"
    )
    stats["total_assignments"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM submissions"
    )
    stats["total_submissions"] = cursor.fetchone()[0]

    return stats


# ==========================================================
# LECTURER ANALYTICS
# ==========================================================

def get_lecturer_stats():

    stats = {}

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM assignments
        """
    )
    stats["assignments"] = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM submissions
        WHERE status='pending'
        """
    )
    stats["pending"] = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM submissions
        WHERE status='graded'
        """
    )
    stats["graded"] = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT AVG(score)
        FROM submissions
        """
    )

    avg = cursor.fetchone()[0]

    stats["average_score"] = round(
        avg if avg else 0,
        2
    )

    return stats


# ==========================================================
# STUDENT ANALYTICS
# ==========================================================

def get_student_stats(
    student_id
):

    stats = {}

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM submissions
        WHERE student_id=?
        """,
        (student_id,)
    )

    stats["submitted"] = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT AVG(score)
        FROM submissions
        WHERE student_id=?
        """,
        (student_id,)
    )

    avg = cursor.fetchone()[0]

    stats["average_score"] = round(
        avg if avg else 0,
        2
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM comments
        WHERE submission_id IN
        (
            SELECT id
            FROM submissions
            WHERE student_id=?
        )
        """,
        (student_id,)
    )

    stats["comments"] = cursor.fetchone()[0]

    return stats


# ==========================================================
# GRADE DISTRIBUTION
# ==========================================================

def get_grade_distribution():

    query = """
    SELECT score
    FROM submissions
    WHERE score IS NOT NULL
    """

    return pd.read_sql_query(
        query,
        conn
    )


# ==========================================================
# SUBMISSION TREND
# ==========================================================

def get_submission_trend():

    query = """
    SELECT
        DATE(submitted_at) as date,
        COUNT(*) as total
    FROM submissions
    GROUP BY DATE(submitted_at)
    ORDER BY DATE(submitted_at)
    """

    return pd.read_sql_query(
        query,
        conn
    )


# ==========================================================
# EXPORT GRADES
# ==========================================================

def export_grades():

    query = """
    SELECT
        id,
        assignment_id,
        student_id,
        score,
        feedback,
        status
    FROM submissions
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    filename = "grades_export.csv"

    df.to_csv(
        filename,
        index=False
    )

    return filename


# ==========================================================
# SEARCH SUBMISSIONS
# ==========================================================

def search_submissions(
    keyword
):

    query = """
    SELECT *
    FROM submissions
    WHERE extracted_text
    LIKE ?
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(f"%{keyword}%",)
    )


# ==========================================================
# DEFAULT ADMIN ACCOUNT
# ==========================================================

cursor.execute(
    """
    SELECT *
    FROM users
    WHERE username='admin'
    """
)

admin = cursor.fetchone()

if admin is None:

    register_user(
        username="admin",
        password="admin123",
        role="admin"
    )

    print(
        "✅ Default Admin Created"
    )


# ==========================================================
# FINAL DATABASE COMMIT
# ==========================================================

conn.commit()

print("✅ Backend Section 4 Loaded")
print("✅ Backend.py v3 Ready")
