# Student Performance Analysis System

A database-driven Streamlit application for Chandigarh University BCA student performance analysis.

## Quick start on Windows

```powershell
cd C:\Python-projects\student_performance_analysis
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit. Click **Load demo dataset** to populate realistic records.

## Features

- SQLite students, subjects and performance tables with foreign keys and validation.
- Dashboard KPIs, leaderboard, subject averages and grade distribution.
- Student CRUD, marks entry, automatic totals, percentage, grade and pass/fail status.
- Analytics for subject strengths, improvement candidates, personalised recommendations and a lightweight trend forecast.
- Plotly bar, pie, histogram and comparison charts.
- Excel and PDF report downloads.
- Dark responsive UI with Amber Saxena branding.

## Project map

`app.py` contains the Streamlit pages; `database.py` handles SQLite; `analysis.py` contains data logic; `visualization.py` contains Plotly factories; `report_generator.py` produces exports. The generated database is stored in `database/student_performance.db`.

## Viva notes

The prediction is intentionally transparent: a linear trend is fitted to semester averages with NumPy. It is an educational baseline, not a production admissions model.
