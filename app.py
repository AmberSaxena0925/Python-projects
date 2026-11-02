import streamlit as st
import pandas as pd
from pathlib import Path
import database as db
import analysis
import visualization as viz
from report_generator import export_excel, export_pdf

st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide")
db.init_db()
if st.sidebar.button("Load demo dataset", use_container_width=True):
    db.seed_demo_data()
    st.sidebar.success("Demo records are ready.")
    st.rerun()

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 15% 5%, #172554 0, #080d1b 38%, #050816 100%); color:#e5e7eb;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0b1225,#111827); border-right:1px solid #263858;}
.block-container {padding-top:1.5rem; max-width:1500px;}
.hero {padding:24px 28px;border:1px solid #263d66;border-radius:18px;
background:linear-gradient(120deg,rgba(30,64,175,.45),rgba(88,28,135,.28)); margin-bottom:18px;}
.dev-ribbon {position:fixed;right:18px;top:12px;z-index:999;background:linear-gradient(120deg,#2563eb,#7c3aed);
padding:10px 16px;border-radius:0 0 12px 12px;color:white;font-size:11px;font-weight:800;
box-shadow:0 8px 24px #0008;letter-spacing:.5px;}
.metric-card {background:linear-gradient(145deg,#111c35,#101827);border:1px solid #293b5d;
padding:18px;border-radius:16px;min-height:112px;}
.metric-label {color:#9caecb;font-size:12px;text-transform:uppercase;letter-spacing:1px;}
.metric-value {font-size:29px;font-weight:800;color:#f8fafc;margin-top:7px;}
div.stButton>button {border-radius:10px;border:1px solid #3b82f6;}
footer {visibility:hidden;}
</style>
<div class="dev-ribbon">✦ DEVELOPED BY AMBER SAXENA · UID 24BCA10021</div>
<div class="hero"><h1>🎓 Student Performance Analysis System</h1>
<p>Academic intelligence · Student records · Performance insights · Reports</p>
<b>Amber Saxena</b> &nbsp; | &nbsp; BCA · Chandigarh University · 24BCA1-A</div>
""", unsafe_allow_html=True)

def load_data():
    return db.query_df("""SELECT p.performance_id,s.student_id,s.name,s.uid,s.section,s.email,
        p.semester,sub.subject_id,sub.subject_name,sub.subject_code,
        p.internal_marks,p.external_marks,p.total_marks,p.percentage,p.grade,p.result
        FROM Performance p JOIN Students s ON p.student_id=s.student_id
        JOIN Subjects sub ON p.subject_id=sub.subject_id ORDER BY s.name, p.semester, sub.subject_name""")

data = load_data()
students = db.query_df("SELECT * FROM Students ORDER BY name")
subjects = db.query_df("SELECT * FROM Subjects ORDER BY subject_name")

pages = ["Overview","Students","Marks & Subjects","Performance Analysis","Reports","About"]
page = st.sidebar.radio("NAVIGATION", pages)
st.sidebar.markdown("---")
st.sidebar.markdown("**DEVELOPED BY AMBER SAXENA**")
st.sidebar.caption("BCA | Chandigarh University\nUID: 24BCA10021")
st.sidebar.caption("Section: 24BCA1-A")

if page == "Overview":
    st.subheader("Class overview")
    summary = analysis.class_summary(data)
    total_students = len(students)
    cols = st.columns(5)
    metrics = [("Students",total_students),("Average score",f"{summary['average']}%"),
               ("Highest",f"{summary['highest']}%"),("Lowest",f"{summary['lowest']}%"),
               ("Pass rate",f"{summary['pass_rate']}%")]
    for col,(label,value) in zip(cols,metrics):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
    st.write("")
    if data.empty:
        st.info("No marks found. Load demo data or add students, subjects and marks from the sidebar pages.")
    else:
        left,right = st.columns(2)
        with left: st.plotly_chart(viz.subject_average(data),use_container_width=True)
        with right: st.plotly_chart(viz.grade_pie(data),use_container_width=True)
        st.plotly_chart(viz.marks_histogram(data),use_container_width=True)
        st.markdown("#### Top performers")
        st.dataframe(analysis.student_ranking(data).head(5),use_container_width=True,hide_index=True)

elif page == "Students":
    st.subheader("Student management")
    with st.expander("➕ Add a student",expanded=True):
        with st.form("add_student"):
            c1,c2,c3 = st.columns(3)
            name=c1.text_input("Full name")
            uid=c2.text_input("University UID")
            section=c3.text_input("Section",value="24BCA1-A")
            semester=c1.number_input("Current semester",1,8,3)
            email=c2.text_input("Email")
            submitted=st.form_submit_button("Save student",type="primary")
            if submitted:
                if not name.strip() or not uid.strip():
                    st.error("Name and UID are required.")
                else:
                    try:
                        db.add_student(name,uid,section,semester,email); st.success("Student added."); st.rerun()
                    except Exception as e: st.error(f"Could not add student: {e}")
    st.markdown("#### Search and manage records")
    q=st.text_input("Search by student name or UID")
    shown=students
    if q: shown=students[students.name.str.contains(q,case=False,na=False)|students.uid.str.contains(q,case=False,na=False)]
    st.dataframe(shown,use_container_width=True,hide_index=True)
    if not shown.empty:
        opts={f"{r['name']} · {r['uid']}":int(r["student_id"]) for _,r in shown.iterrows()}
        chosen=st.selectbox("Select a student to edit or delete",list(opts))
        sid=opts[chosen]
        current=students[students.student_id==sid].iloc[0]
        with st.form("edit_student"):
            c1,c2,c3=st.columns(3)
            ename=c1.text_input("Name",current["name"])
            euid=c2.text_input("UID",current["uid"])
            esec=c3.text_input("Section",current["section"])
            esem=c1.number_input("Semester",1,8,int(current["semester"]))
            eemail=c2.text_input("Email",current["email"] or "")
            save=st.form_submit_button("Update student")
            if save:
                try: db.update_student(sid,ename,euid,esec,esem,eemail); st.success("Updated."); st.rerun()
                except Exception as e: st.error(str(e))
        if st.button("Delete selected student",type="secondary"):
            db.delete_student(sid); st.success("Student and linked marks deleted."); st.rerun()
        profile=data[data.student_id==sid]
        if not profile.empty:
            st.markdown("#### Individual profile")
            st.dataframe(profile[["semester","subject_name","total_marks","percentage","grade","result"]],use_container_width=True,hide_index=True)
            for note in analysis.student_insights(profile): st.info(note)

elif page == "Marks & Subjects":
    st.subheader("Marks and subject management")
    with st.expander("Add a subject"):
        with st.form("add_subject"):
            a,b,c=st.columns(3)
            sname=a.text_input("Subject name")
            scode=b.text_input("Subject code")
            maximum=c.number_input("Maximum marks",min_value=1.0,value=100.0)
            if st.form_submit_button("Add subject"):
                if not sname.strip(): st.error("Subject name is required.")
                else:
                    try: db.add_subject(sname,scode,maximum); st.success("Subject added."); st.rerun()
                    except Exception as e: st.error(str(e))
    if students.empty or subjects.empty:
        st.warning("Add at least one student and one subject before recording marks.")
    else:
        with st.form("marks_form"):
            c1,c2,c3=st.columns(3)
            student_map={f"{r['name']} ({r['uid']})":int(r.student_id) for _,r in students.iterrows()}
            subject_map={f"{r['subject_name']} ({r['subject_code'] or 'no code'})":int(r.subject_id) for _,r in subjects.iterrows()}
            student_key=c1.selectbox("Student",list(student_map))
            subject_key=c2.selectbox("Subject",list(subject_map))
            sem=c3.number_input("Semester",1,8,3)
            subject_row=subjects[subjects.subject_id==subject_map[subject_key]].iloc[0]
            internal=c1.number_input("Internal marks",0.0,float(subject_row.maximum_marks),0.0)
            external=c2.number_input("External marks",0.0,float(subject_row.maximum_marks),0.0)
            maximum=float(subject_row.maximum_marks)
            if internal+external > maximum: st.warning(f"Combined marks cannot exceed {maximum}.")
            if st.form_submit_button("Save marks",type="primary"):
                if internal+external>maximum: st.error("Combined marks exceed maximum marks.")
                else:
                    pct=(internal+external)/maximum*100
                    grade=analysis.grade_for(pct)
                    try:
                        db.save_performance(student_map[student_key],subject_map[subject_key],sem,internal,external,grade,"Pass" if pct>=40 else "Fail")
                        st.success(f"Marks saved · {pct:.1f}% · Grade {grade}"); st.rerun()
                    except Exception as e: st.error(str(e))
    st.markdown("#### Recorded marks")
    if not data.empty:
        st.dataframe(data[["name","uid","semester","subject_name","internal_marks","external_marks","total_marks","percentage","grade","result"]],use_container_width=True,hide_index=True)
        ids=data.performance_id.tolist()
        del_id=st.selectbox("Select a marks record to delete",ids)
        if st.button("Delete marks record"):
            db.execute("DELETE FROM Performance WHERE performance_id=?",(int(del_id),)); st.success("Record deleted."); st.rerun()

elif page == "Performance Analysis":
    st.subheader("Performance intelligence")
    if data.empty: st.info("Add performance records to unlock analysis.")
    else:
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(viz.subject_bar(data),use_container_width=True)
        with c2: st.plotly_chart(viz.grade_pie(data),use_container_width=True)
        st.plotly_chart(viz.semester_line(data),use_container_width=True)
        st.markdown("#### Student leaderboard")
        st.dataframe(analysis.student_ranking(data),use_container_width=True,hide_index=True)
        st.markdown("#### Subject analysis")
        st.dataframe(analysis.subject_summary(data),use_container_width=True,hide_index=True)
        st.markdown("#### Students requiring attention")
        needs=data.groupby(["student_id","name","uid"],as_index=False).percentage.mean()
        needs=needs[needs.percentage<60].sort_values("percentage")
        if needs.empty: st.success("No student is currently below the 60% support threshold.")
        else: st.dataframe(needs,use_container_width=True,hide_index=True)
        selected=st.selectbox("Generate personalised insight for",data.name.drop_duplicates().tolist())
        for note in analysis.student_insights(data[data.name==selected]): st.info(note)
        hist=data.groupby(["student_id","name","semester"],as_index=False).percentage.mean()
        if len(hist[hist.name==selected])>=2:
            pred=analysis.predict_next_score(hist[hist.name==selected])
            if pred is not None: st.metric("Estimated next-semester score",f"{pred:.1f}%",help="A simple linear trend estimate, not a guaranteed result.")
        else: st.caption("Add marks in at least two semesters to estimate a trend.")

elif page == "Reports":
    st.subheader("Reports and exports")
    if data.empty: st.info("No records available to export.")
    else:
        st.write(f"**{len(data)}** performance records are ready.")
        st.dataframe(data,use_container_width=True,hide_index=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Generate class PDF",use_container_width=True):
                path=export_pdf("Class Performance Report",data)
                st.session_state["pdf_path"]=str(path)
            if st.session_state.get("pdf_path"):
                p=Path(st.session_state["pdf_path"])
                st.download_button("⬇ Download PDF",p.read_bytes(),file_name=p.name,mime="application/pdf")
        with c2:
            if st.button("Prepare Excel workbook",use_container_width=True):
                path=export_excel(data)
                st.session_state["xlsx_path"]=str(path)
            if st.session_state.get("xlsx_path"):
                p=Path(st.session_state["xlsx_path"])
                st.download_button("⬇ Download Excel",p.read_bytes(),file_name=p.name,mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        csv=data.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download CSV",csv,"student_performance.csv","text/csv")

else:
    st.subheader("Project overview")
    st.markdown("""
    **Student Performance Analysis System** is a Python + Streamlit application for maintaining academic records,
    analysing marks, identifying learning gaps and producing reports.

    **Developer:** Amber Saxena · **UID:** 24BCA10021  
    **Course:** Bachelor of Computer Applications · **University:** Chandigarh University  
    **Section:** 24BCA1-A

    **Technology:** Python 3, Streamlit, Pandas, NumPy, SQLite, Plotly, Matplotlib/Seaborn-compatible analysis,
    ReportLab and OpenPyXL.

    **How grades work:** A+ (90+), A (80–89), B+ (70–79), B (60–69), C (50–59), D (40–49), F (below 40).
    The grading helper is centralised in `analysis.py`, so the scale can be changed easily.

    **Prediction note:** The next-semester estimate uses a basic linear trend over recorded semester averages.
    It is an educational indicator, not a validated high-stakes prediction model.
    """)

st.markdown("<hr><center><small>Designed & Developed by Amber Saxena | BCA | Chandigarh University | 2026</small></center>",unsafe_allow_html=True)
