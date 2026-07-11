# ==========================================================
# AI ACADEMIC EVALUATION SYSTEM
# APP.PY V3
# SECTION 1
# IMPORTS + PAGE CONFIG + CSS + SESSION STATE
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import os

from backend import (
    login_user,
    register_user,

    add_course,
    assign_lecturer,
    get_all_courses,

    create_assignment,
    get_course_assignments,

    submit_assignment,
    get_submissions,
    get_submission,
    get_student_submissions,

    grade_submission,
    override_grade,

    add_comment,
    get_comments,

    get_admin_stats,
    get_lecturer_stats,
    get_student_stats,

    get_grade_distribution,
    get_submission_trend,

    export_grades
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Assignment Grading  System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* Main App */
.main {
    background-color: #0e1117;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 12px;
}

/* DataFrames */
.stDataFrame {
    border-radius: 12px;
}

/* Page spacing */
.block-container {
    padding-top: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid #30363d;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE
# ==========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


# ==========================================================
# KPI CARDS HELPER
# ==========================================================

def metric_cards(
    value1,
    value2,
    value3,
    value4,
    label1,
    label2,
    label3,
    label4
):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label1, value1)
    col2.metric(label2, value2)
    col3.metric(label3, value3)
    col4.metric(label4, value4)


print("✅ App Section 1 Loaded")

# ==========================================================
# SECTION 2
# LOGIN PAGE + SIDEBAR + NAVIGATION
# ==========================================================


# ==========================================================
# LOGIN PAGE
# ==========================================================

def login_page():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.title("🎓 AI Assignment Grading System")

        st.markdown(
            "### AI Assignment Evaluation"
        )

        st.markdown("---")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login"
        ):

            user = login_user(
                username,
                password
            )

            if user:

                st.session_state.logged_in = True

                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.role = user[3]

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )


# ==========================================================
# SIDEBAR
# ==========================================================

def sidebar():

    with st.sidebar:

        st.title(
            "🎓 AI Evaluation"
        )

        st.markdown("---")

        st.write(
            f"👤 {st.session_state.username}"
        )

        st.write(
            f"🔑 {st.session_state.role}"
        )

        st.markdown("---")

        if st.button(
            "🚪 Logout"
        ):

            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.role = None

            st.rerun()


# ==========================================================
# NAVIGATION ROUTER
# ==========================================================

def navigation():

    sidebar()

    role = st.session_state.role

    if role == "admin":

        admin_dashboard()

    elif role == "lecturer":

        lecturer_dashboard()

    elif role == "student":

        student_dashboard()


print("✅ App Section 2 Loaded")

# ==========================================================
# SECTION 3
# ADMIN DASHBOARD
# ==========================================================

def admin_dashboard():

    st.title("📊 Admin Dashboard")

    stats = get_admin_stats()

    metric_cards(
        stats["total_users"],
        stats["total_courses"],
        stats["total_assignments"],
        stats["total_submissions"],
        "Users",
        "Courses",
        "Assignments",
        "Submissions"
    )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📚 Courses",
            "👨‍🏫 Lecturers",
            "🎓 Students",
            "📋 View Courses"
        ]
    )

    # ======================================================
    # CREATE COURSE
    # ======================================================

    with tab1:

        st.subheader(
            "Create New Course"
        )

        course_code = st.text_input(
            "Course Code",
            key="course_code"
        )

        title = st.text_input(
            "Course Title",
            key="course_title"
        )

        dept = st.text_input(
            "Department",
            key="course_dept"
        )

        level = st.text_input(
            "Level",
            key="course_level"
        )

        lecturer_id = st.text_input(
            "Lecturer ID",
            key="course_lecturer"
        )

        if st.button(
            "Create Course",
            key="create_course_btn"
        ):

            try:

                add_course(
                    course_code,
                    title,
                    dept,
                    level,
                    lecturer_id
                )

                st.success(
                    "Course Created Successfully"
                )

            except Exception as e:

                st.error(str(e))

    # ======================================================
    # REGISTER LECTURER
    # ======================================================

    with tab2:

        st.subheader(
            "Register Lecturer"
        )

        username = st.text_input(
            "Username",
            key="lec_user"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="lec_pass"
        )

        if st.button(
            "Register Lecturer",
            key="register_lec_btn"
        ):

            success = register_user(
                username,
                password,
                "lecturer"
            )

            if success:

                st.success(
                    "Lecturer Registered"
                )

            else:

                st.error(
                    "Registration Failed"
                )

    # ======================================================
    # REGISTER STUDENT
    # ======================================================

    with tab3:

        st.subheader(
            "Register Student"
        )

        username = st.text_input(
            "Username",
            key="stud_user"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="stud_pass"
        )

        matric = st.text_input(
            "Matric Number"
        )

        dept = st.text_input(
            "Department"
        )

        faculty = st.text_input(
            "Faculty"
        )

        if st.button(
            "Register Student",
            key="register_student_btn"
        ):

            success = register_user(
                username,
                password,
                "student",
                matric,
                dept,
                faculty
            )

            if success:

                st.success(
                    "Student Registered"
                )

            else:

                st.error(
                    "Registration Failed"
                )

    # ======================================================
    # VIEW COURSES
    # ======================================================

    with tab4:

        st.subheader(
            "Available Courses"
        )

        try:

            courses = get_all_courses()

            st.dataframe(
                courses,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                str(e)
            )


print("✅ App Section 3 Loaded")

# ==========================================================
# SECTION 4
# LECTURER DASHBOARD
# ==========================================================

def lecturer_dashboard():

    st.title("👨‍🏫 Lecturer Dashboard")

    stats = get_lecturer_stats()

    metric_cards(
        stats["assignments"],
        stats["pending"],
        stats["graded"],
        stats["average_score"],
        "Assignments",
        "Pending",
        "Graded",
        "Average Score"
    )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📚 Assignments",
            "➕ Create Assignment",
            "📄 Submissions",
            "📊 Analytics"
        ]
    )

    # ======================================================
    # VIEW ASSIGNMENTS
    # ======================================================

    with tab1:

        st.subheader(
            "Course Assignments"
        )

        course_id = st.text_input(
            "Course ID",
            key="view_course_id"
        )

        if st.button(
            "Load Assignments"
        ):

            try:

                assignments = get_course_assignments(
                    course_id
                )

                st.dataframe(
                    assignments,
                    use_container_width=True
                )

            except Exception as e:

                st.error(str(e))

    # ======================================================
    # CREATE ASSIGNMENT
    # ======================================================

    with tab2:

        st.subheader(
            "Create Assignment"
        )

        course_id = st.text_input(
            "Course ID",
            key="create_course_id"
        )

        title = st.text_input(
            "Assignment Title"
        )

        instructions = st.text_area(
            "Instructions"
        )

        rubric = st.text_area(
            "Rubric"
        )

        deadline = st.date_input(
            "Deadline"
        )

        total_score = st.number_input(
            "Total Score",
            min_value=1,
            max_value=100,
            value=100
        )

        if st.button(
            "Create Assignment"
        ):

            try:

                create_assignment(
                    course_id,
                    title,
                    instructions,
                    rubric,
                    str(deadline),
                    total_score,
                    st.session_state.user_id
                )

                st.success(
                    "Assignment Created Successfully"
                )

            except Exception as e:

                st.error(str(e))

    # ======================================================
    # SUBMISSIONS
    # ======================================================

    with tab3:

        st.subheader(
            "Assignment Submissions"
        )

        assignment_id = st.text_input(
            "Assignment ID"
        )

        if st.button(
            "Load Submissions"
        ):

            try:

                submissions = get_submissions(
                    assignment_id
                )

                st.dataframe(
                    submissions,
                    use_container_width=True
                )

            except Exception as e:

                st.error(str(e))

        st.markdown("---")

        st.subheader(
            "Review Submission"
        )

        submission_id = st.number_input(
            "Submission ID",
            min_value=1,
            value=1
        )

        if st.button(
            "Load Submission"
        ):

            submission = get_submission(
                submission_id
            )

            if submission:

                st.success(
                    "Submission Loaded"
                )

                st.write(
                    f"📄 File: {submission[3]}"
                )

                st.text_area(
                    "Extracted Text",
                    submission[4],
                    height=250
                )

            else:

                st.warning(
                    "Submission Not Found"
                )

        st.markdown("---")

        st.subheader(
            "🤖 AI Grading"
        )

        course_name = st.text_input(
            "Course Name"
        )

        rubric_text = st.text_area(
            "Grading Rubric"
        )

        if st.button(
            "Grade With AI"
        ):

            result = grade_submission(
                submission_id,
                course_name,
                rubric_text
            )

            if result:

                st.success(
                    "AI Grading Complete"
                )

                st.metric(
                    "Score",
                    result["score"]
                )

                st.text_area(
                    "Feedback",
                    result["feedback"],
                    height=200
                )

            else:

                st.error(
                    "Grading Failed"
                )

        st.markdown("---")

        st.subheader(
            "Manual Override"
        )

        override_score = st.number_input(
            "Override Score",
            min_value=0,
            max_value=100,
            value=50
        )

        override_feedback = st.text_area(
            "Override Feedback"
        )

        if st.button(
            "Save Override"
        ):

            try:

                override_grade(
                    submission_id,
                    override_score,
                    override_feedback
                )

                st.success(
                    "Grade Updated"
                )

            except Exception as e:

                st.error(str(e))

    # ======================================================
    # ANALYTICS
    # ======================================================

    with tab4:

        st.subheader(
            "Grade Analytics"
        )

        try:

            grades = get_grade_distribution()

            if len(grades) > 0:

                fig = px.histogram(
                    grades,
                    x="score",
                    nbins=10,
                    title="Grade Distribution"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        except Exception as e:

            st.error(str(e))

        st.markdown("---")

        try:

            trend = get_submission_trend()

            if len(trend) > 0:

                fig2 = px.line(
                    trend,
                    x="date",
                    y="total",
                    markers=True,
                    title="Submission Trend"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

        except Exception as e:

            st.error(str(e))

        st.markdown("---")

        if st.button(
            "Export Grades CSV"
        ):

            try:

                file_name = export_grades()

                with open(
                    file_name,
                    "rb"
                ) as f:

                    st.download_button(
                        "Download CSV",
                        f,
                        file_name=file_name
                    )

            except Exception as e:

                st.error(str(e))


print("✅ App Section 4 Loaded")

# ==========================================================
# SECTION 5
# STUDENT DASHBOARD + MAIN ENTRY POINT
# ==========================================================

def student_dashboard():

    st.title("🎓 Student Dashboard")

    stats = get_student_stats(
        st.session_state.user_id
    )

    metric_cards(
        stats["submitted"],
        stats["average_score"],
        stats["comments"],
        "Active",
        "Submissions",
        "Average Score",
        "Comments",
        "Status"
    )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📤 Submit Assignment",
            "📄 My Submissions",
            "💬 Comments",
            "📈 Performance"
        ]
    )

    # ======================================================
    # SUBMIT ASSIGNMENT
    # ======================================================

    with tab1:

        st.subheader(
            "Submit Assignment"
        )

        assignment_id = st.number_input(
            "Assignment ID",
            min_value=1,
            value=1
        )

        uploaded_file = st.file_uploader(
            "Upload PDF or DOCX",
            type=["pdf", "docx"]
        )

        if uploaded_file:

            st.success(
                f"Selected: {uploaded_file.name}"
            )

            st.info(
                f"Size: {round(uploaded_file.size/1024,2)} KB"
            )

        if st.button(
            "Submit Assignment"
        ):

            if uploaded_file is None:

                st.error(
                    "Please upload a file."
                )

            else:

                os.makedirs(
                    "uploads",
                    exist_ok=True
                )

                save_path = os.path.join(
                    "uploads",
                    uploaded_file.name
                )

                with open(
                    save_path,
                    "wb"
                ) as f:

                    f.write(
                        uploaded_file.getbuffer()
                    )

                submit_assignment(
                    assignment_id,
                    st.session_state.user_id,
                    save_path
                )

                st.success(
                    "Assignment Submitted Successfully"
                )

    # ======================================================
    # MY SUBMISSIONS
    # ======================================================

    with tab2:

        st.subheader(
            "My Submission History"
        )

        try:

            submissions = get_student_submissions(
                st.session_state.user_id
            )

            st.dataframe(
                submissions,
                use_container_width=True
            )

        except Exception as e:

            st.error(str(e))

    # ======================================================
    # COMMENTS
    # ======================================================

    with tab3:

        st.subheader(
            "Comments & Feedback"
        )

        submission_id = st.number_input(
            "Submission ID",
            min_value=1,
            value=1,
            key="comment_submission_id"
        )

        if st.button(
            "Load Comments"
        ):

            try:

                comments = get_comments(
                    submission_id
                )

                st.dataframe(
                    comments,
                    use_container_width=True
                )

            except Exception as e:

                st.error(str(e))

        st.markdown("---")

        reply = st.text_area(
            "Reply"
        )

        if st.button(
            "Send Reply"
        ):

            try:

                add_comment(
                    0,
                    submission_id,
                    st.session_state.user_id,
                    reply
                )

                st.success(
                    "Reply Sent"
                )

            except Exception as e:

                st.error(str(e))

    # ======================================================
    # PERFORMANCE
    # ======================================================

    with tab4:

        st.subheader(
            "Performance Analytics"
        )

        try:

            submissions = get_student_submissions(
                st.session_state.user_id
            )

            if len(submissions) > 0:

                if "score" in submissions.columns:

                    fig = px.line(
                        submissions,
                        x="submitted_at",
                        y="score",
                        markers=True,
                        title="Score Progress"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                st.dataframe(
                    submissions,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No submissions available."
                )

        except Exception as e:

            st.error(str(e))


# ==========================================================
# MAIN APPLICATION
# ==========================================================

if not st.session_state.logged_in:

    login_page()

else:

    navigation()


print("✅ App Section 5 Loaded")
print("✅ app.py v3 Ready")
