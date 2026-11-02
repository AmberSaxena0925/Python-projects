import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

THEME = "plotly_dark"


def subject_bar(data: pd.DataFrame):
    return px.bar(data, x="subject_name", y="average_percentage", color="average_percentage", color_continuous_scale="Blues", labels={"average_percentage": "Average %", "subject_name": "Subject"}, template=THEME)


def grade_pie(data: pd.DataFrame):
    return px.pie(data, names="grade", values="count", hole=0.55, color_discrete_sequence=px.colors.sequential.Blues_r, template=THEME)


def marks_histogram(data: pd.DataFrame):
    return px.histogram(data, x="percentage", nbins=10, color_discrete_sequence=["#5b8cff"], template=THEME, labels={"percentage": "Percentage"})


def comparison_chart(data: pd.DataFrame):
    return px.bar(data, x="name", y="average_percentage", color="average_percentage", color_continuous_scale="Tealgrn", template=THEME, labels={"average_percentage": "Average %", "name": "Student"})


def semester_line(data: pd.DataFrame):
    if data.empty:
        return go.Figure()
    return px.line(data, x="semester", y="percentage", color="name", markers=True, template=THEME, labels={"percentage": "Average %", "semester": "Semester"})
