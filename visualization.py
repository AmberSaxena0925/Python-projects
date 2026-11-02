"""Plotly chart builders used by the Streamlit interface."""
import plotly.express as px
import plotly.graph_objects as go

DARK = "plotly_dark"

def subject_bar(df):
    return px.bar(df, x="subject_name", y="percentage", color="name",
                  barmode="group", title="Subject-wise student marks",
                  labels={"percentage":"Score (%)","subject_name":"Subject"}, template=DARK)

def grade_pie(df):
    counts = df.grade.value_counts().rename_axis("Grade").reset_index(name="Students")
    return px.pie(counts, names="Grade", values="Students", hole=.55,
                  title="Grade distribution", template=DARK)

def semester_line(df):
    grouped = df.groupby(["semester","name"],as_index=False).percentage.mean()
    return px.line(grouped, x="semester", y="percentage", color="name", markers=True,
                   title="Semester-wise progress", template=DARK)

def marks_histogram(df):
    return px.histogram(df, x="percentage", nbins=12, title="Marks distribution",
                        labels={"percentage":"Score (%)"}, template=DARK)

def subject_average(df):
    data = df.groupby("subject_name",as_index=False).percentage.mean().sort_values("percentage")
    return px.bar(data, x="percentage", y="subject_name", orientation="h",
                  title="Class average by subject", template=DARK)
