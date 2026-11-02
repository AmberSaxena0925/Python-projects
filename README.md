# Student Performance Analysis System

A local academic records and performance analysis application built with Python, Streamlit, SQLite, Pandas, NumPy, and Plotly. Manage student and subject records, record marks, review performance insights, and export reports from one dashboard.

## Features

- **Overview dashboard** with student count, average score, highest and lowest scores, and pass rate.
- **Student management** to add, search, update, and delete student profiles.
- **Subject management** and semester based marks entry.
- **Automatic calculations** for totals, percentages, grades, and pass or fail results.
- **Performance analysis** with subject summaries, grade distribution, semester trends, score histograms, student rankings, and individual insights.
- **Report exports** in PDF, Excel, and CSV formats.
- **SQLite storage** created locally by the application.
- **Demo dataset** to explore the dashboard immediately.

## Requirements

- Python 3.10 or newer
- `pip`

## Getting started

### Windows (PowerShell)

```powershell
git clone <repository-url>
cd student_performance_analysis
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell prevents virtual environment activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead.

### macOS or Linux

```bash
git clone <repository-url>
cd student_performance_analysis
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit prints a local URL after startup, usually <http://localhost:8501>.

> Replace `<repository-url>` with this repository's Git URL when publishing the project on GitHub.

## Using the application

1. Start the application using the command above.
2. Choose **Load demo dataset** in the sidebar to populate sample students, subjects, and marks. The sample data is only inserted when the database has no student records.
3. Use **Students** to manage student profiles.
4. Use **Marks & Subjects** to add subjects and enter semester marks.
5. Review charts and insights under **Performance Analysis**.
6. Export reports from **Reports**.

## Project structure

```text
student_performance_analysis/
├── app.py                 # Streamlit interface and navigation
├── analysis.py            # Grades, summaries, rankings, and insights
├── database.py            # SQLite schema and data operations
├── visualization.py       # Plotly charts
├── report_generator.py    # PDF, Excel, and CSV exports
├── requirements.txt       # Python dependencies
├── database/              # Local SQLite database is created here
├── assets/                # Static assets
└── reports/               # Generated report files
```

## Data and calculations

The local database is stored at `database/student_performance.db` and is created automatically when the application starts. Student deletion cascades to related performance records. Keep a copy of the database file if you need to back up your records.

- **Total marks** = internal marks + external marks
- **Percentage** = total marks / subject maximum marks × 100
- **Pass** = percentage ≥ 40%; otherwise **Fail**
- **Grades:** A+ ≥ 90, A ≥ 80, B+ ≥ 70, B ≥ 60, C ≥ 50, D ≥ 40, F < 40

Grade thresholds are defined by `DEFAULT_SCALE` in `analysis.py`.

## Tech stack

- [Python](https://www.python.org/) and [Streamlit](https://streamlit.io/) for the application
- [SQLite](https://www.sqlite.org/) for local data storage
- [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/) for analysis
- [Plotly](https://plotly.com/python/) for interactive charts
- ReportLab and OpenPyXL for PDF and Excel exports

## Notes

The next-semester estimate is a simple linear trend over prior semester averages. It is an educational indicator and should not be treated as a validated prediction. This project is intended for local demonstration; it does not include user authentication or role-based access controls.

## Author

**Amber Saxena** · BCA, Chandigarh University · UID 24BCA10021
