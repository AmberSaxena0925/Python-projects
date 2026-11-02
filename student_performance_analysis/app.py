from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import improvement_candidates, predict_next_score, recommendation, student_averages, subject_averages, grade_distribution
from db import add_student, execute, initialize_database, query_df, save_performance, seed_demo_data
from report_generator import dataframe_excel, student_pdf
from visualization import comparison_chart, grade_pie, marks_histogram, semester_line, subject_bar

st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
initialize_database()

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 85% 10%, #172554 0%, #070b17 42%, #03050a 100%); color: #e5eefc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0c1427,#090c16); border-right: 1px solid #1e3a8a; }
.brand { padding: 1.2rem; border-radius: 18px; background: linear-gradient(135deg,#2563eb,#7c3aed); box-shadow: 0 12px 30px #111827aa; margin-bottom: 1.2rem; }
.brand h3 { margin: 0; color: white; letter-spacing: .06em; font-size: 1.05rem; }
.brand p { margin: .35rem 0 0; color: #dbeafe; font-size: .82rem; }
.hero { padding: 1.6rem; border-radius: 22px; background: linear-gradient(110deg,#111827cc,#172554aa); border: 1px solid #1d4ed855; margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2.3rem; } .hero p { color: #a5b4fc; }
.metric { padding: 1rem; border-radius: 16px; background: linear-gradient(145deg,#0f172a,#111c36); border: 1px solid #1e40af66; }
footer { visibility: visible; text-align: center; color: #64748b; padding: 2rem 0 1rem; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="brand"><h3>✦ DEVELOPED BY AMBER SAXENA</h3><p>BCA | Chandigarh University<br>UID: 24BCA10021</p></div>', unsafe_allow_html=True)
page = st.sidebar.radio("Workspace", ["Dashboard", "Students", "Marks", "Analytics", "Reports", "Settings"], index=0)
if st.sidebar.button("Load demo dataset", use_container_width=True):
    seed_demo_data(); st.sidebar.success("Demo records are ready."); st.rerun()

performance = query_df("SELECT p.*, s.name, s.uid, s.semester AS student_semester, sub.subject_name, sub.subject_code FROM performance p JOIN students s ON s.student_id=p.student_id JOIN subjects sub ON sub.subject_id=p.subject_id")
students = query_df("SELECT * FROM students ORDER BY name")
subjects = query_df("SELECT * FROM subjects ORDER BY subject_name")
averages = student_averages(performance) if not performance.empty else pd.DataFrame(columns=["student_id", "name", "uid", "average_percentage", "subjects", "passed"])

if page == "Dashboard":
    st.markdown('<div class="hero"><h1>Student Performance Command Center</h1><p>Turn academic records into clear, timely action for every learner.</p></div>', unsafe_allow_html=True)
    total_students = len(students); avg = performance.percentage.mean() if not performance.empty else 0; highest = performance.percentage.max() if not performance.empty else 0; pass_rate = (performance.result.eq("Pass").mean() * 100) if not performance.empty else 0
    cols = st.columns(4)
    for col, title, value, icon in zip(cols, ["Students", "Class average", "Highest score", "Pass rate"], [total_students, f"{avg:.1f}%", f"{highest:.1f}%", f"{pass_rate:.1f}%"], ["👥", "📈", "🏆", "✅"]):
        col.markdown(f'<div class="metric"><div>{icon} {title}</div><h2>{value}</h2></div>', unsafe_allow_html=True)
    if performance.empty:
        st.info("Load the demo dataset or add records from the Students and Marks pages.")
    else:
        left, right = st.columns([1.45, 1])
        with left: st.plotly_chart(subject_bar(subject_averages(performance)), use_container_width=True)
        with right: st.plotly_chart(grade_pie(grade_distribution(performance)), use_container_width=True)
        st.subheader("Leaderboard")
        st.dataframe(averages.assign(Rank=range(1, len(averages) + 1))[['Rank','name','uid','average_percentage','passed']].rename(columns={'name':'Student','uid':'UID','average_percentage':'Average %','passed':'Passed subjects'}), use_container_width=True, hide_index=True)
elif page == "Students":
    st.title("Student Management")
    with st.expander("Add new student", expanded=True):
        with st.form("student_form"):
            c1, c2 = st.columns(2); name = c1.text_input("Full name"); uid = c2.text_input("UID"); c3, c4, c5 = st.columns(3); section = c3.text_input("Section", "24BCA1-A"); semester = c4.number_input("Semester", 1, 8, 4); email = c5.text_input("Email"); submitted = st.form_submit_button("Save student", type="primary")
            if submitted:
                if not name.strip() or not uid.strip() or "@" not in email: st.error("Enter a name, UID and valid email.")
                else:
                    try: add_student(name, uid, section, semester, email); st.success("Student added."); st.rerun()
                    except Exception as exc: st.error(f"Could not save record: {exc}")
    search = st.text_input("Search by name or UID")
    filtered = students[students.apply(lambda row: search.lower() in f"{row['name']} {row['uid']}".lower(), axis=1)] if search else students
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    if not filtered.empty:
        selected_uid = st.selectbox("Select a student to view profile", filtered.uid.tolist()); profile = filtered[filtered.uid == selected_uid].iloc[0]; st.info(f"{profile['name']} • {profile['email']} • {profile['section']} • Semester {profile['semester']}")
        if st.button("Delete selected student", type="secondary"):
            execute("DELETE FROM students WHERE student_id = ?", (int(profile.student_id),)); st.success("Student deleted."); st.rerun()
elif page == "Marks":
    st.title("Marks Management")
    if students.empty or subjects.empty: st.warning("Add students and subjects before entering marks.")
    else:
        with st.form("marks_form"):
            student_id = st.selectbox("Student", students.student_id, format_func=lambda value: students.loc[students.student_id == value, "name"].iloc[0]); subject_id = st.selectbox("Subject", subjects.subject_id, format_func=lambda value: subjects.loc[subjects.subject_id == value, "subject_name"].iloc[0]); semester = st.number_input("Semester", 1, 8, 4); internal = st.number_input("Internal marks", 0.0, 40.0, 30.0); external = st.number_input("External marks", 0.0, 60.0, 45.0); save = st.form_submit_button("Save marks", type="primary")
            if save:
                try: save_performance(int(student_id), int(subject_id), int(semester), internal, external); st.success("Marks saved and grade calculated."); st.rerun()
                except Exception as exc: st.error(f"Could not save marks: {exc}")
        st.dataframe(performance, use_container_width=True, hide_index=True)
elif page == "Analytics":
    st.title("Performance Analytics")
    if performance.empty: st.info("Add performance records to unlock analytics.")
    else:
        c1, c2 = st.columns(2); c1.plotly_chart(marks_histogram(performance), use_container_width=True); c2.plotly_chart(comparison_chart(averages.head(10)), use_container_width=True)
        st.subheader("Students needing academic improvement")
        needs_help = improvement_candidates(averages); st.dataframe(needs_help, use_container_width=True, hide_index=True) if not needs_help.empty else st.success("No students are currently below the improvement threshold.")
        st.subheader("Personalised insight")
        selected = st.selectbox("Student", averages.uid.tolist()); selected_id = int(averages.loc[averages.uid == selected, "student_id"].iloc[0]); profile_marks = performance[performance.student_id == selected_id]; weak = profile_marks.loc[profile_marks.percentage < 60, "subject_name"].tolist(); st.info(recommendation(weak)); st.metric("Predicted next score", f"{predict_next_score(profile_marks.groupby('semester').percentage.mean().sort_index().tolist()) or 0:.1f}%")
elif page == "Reports":
    st.title("Reports & Exports")
    if performance.empty: st.info("Load records before generating reports.")
    else:
        st.download_button("Download all performance as Excel", dataframe_excel(performance, "Performance"), "student_performance.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        selected = st.selectbox("Student report", students.uid.tolist()); student = students[students.uid == selected].iloc[0].to_dict(); marks = performance[performance.student_id == student['student_id']]; st.download_button("Download student PDF", student_pdf(student, marks), f"{selected}_report.pdf", "application/pdf")
        st.dataframe(marks, use_container_width=True, hide_index=True)
else:
    st.title("Settings")
    st.write("Grade scale: A+ (90), A (80), B+ (70), B (60), C (50), D (40), F (below 40).")
    st.caption("The scale is implemented in database.py and can be changed in one place for viva/project customisation.")

st.markdown('<footer>Designed & Developed by Amber Saxena | BCA | Chandigarh University | 2026</footer>', unsafe_allow_html=True)
