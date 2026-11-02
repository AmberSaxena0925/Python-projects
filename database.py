"""SQLite persistence layer for Student Performance Analysis System."""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "student_performance.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uid TEXT NOT NULL UNIQUE,
            section TEXT NOT NULL DEFAULT '24BCA1-A',
            semester INTEGER NOT NULL DEFAULT 1 CHECK(semester BETWEEN 1 AND 8),
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS Subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            subject_code TEXT UNIQUE,
            maximum_marks REAL NOT NULL DEFAULT 100 CHECK(maximum_marks > 0)
        );
        CREATE TABLE IF NOT EXISTS Performance (
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES Students(student_id) ON DELETE CASCADE,
            subject_id INTEGER NOT NULL REFERENCES Subjects(subject_id) ON DELETE CASCADE,
            semester INTEGER NOT NULL DEFAULT 1,
            internal_marks REAL NOT NULL DEFAULT 0,
            external_marks REAL NOT NULL DEFAULT 0,
            total_marks REAL NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            result TEXT NOT NULL,
            UNIQUE(student_id, subject_id, semester)
        );
        """)
        con.commit()

def query_df(sql, params=()):
    with get_connection() as con:
        return pd.read_sql_query(sql, con, params=params)

def execute(sql, params=()):
    with get_connection() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid

def add_student(name, uid, section, semester, email=""):
    return execute("INSERT INTO Students(name,uid,section,semester,email) VALUES(?,?,?,?,?)",
                   (name.strip(), uid.strip(), section.strip(), int(semester), email.strip()))

def update_student(student_id, name, uid, section, semester, email=""):
    execute("UPDATE Students SET name=?,uid=?,section=?,semester=?,email=? WHERE student_id=?",
            (name.strip(), uid.strip(), section.strip(), int(semester), email.strip(), int(student_id)))

def delete_student(student_id):
    execute("DELETE FROM Students WHERE student_id=?", (int(student_id),))

def add_subject(name, code, maximum=100):
    return execute("INSERT INTO Subjects(subject_name,subject_code,maximum_marks) VALUES(?,?,?)",
                   (name.strip(), code.strip() or None, float(maximum)))

def save_performance(student_id, subject_id, semester, internal, external, grade, result):
    maximum = query_df("SELECT maximum_marks FROM Subjects WHERE subject_id=?", (int(subject_id),))
    if maximum.empty:
        raise ValueError("Subject not found.")
    total = float(internal) + float(external)
    pct = (total / float(maximum.iloc[0]["maximum_marks"])) * 100
    execute("""INSERT INTO Performance(student_id,subject_id,semester,internal_marks,external_marks,
               total_marks,percentage,grade,result) VALUES(?,?,?,?,?,?,?,?,?)
               ON CONFLICT(student_id,subject_id,semester) DO UPDATE SET
               internal_marks=excluded.internal_marks, external_marks=excluded.external_marks,
               total_marks=excluded.total_marks, percentage=excluded.percentage,
               grade=excluded.grade, result=excluded.result""",
            (int(student_id), int(subject_id), int(semester), float(internal), float(external),
             total, pct, grade, result))

def seed_demo_data():
    init_db()
    if not query_df("SELECT * FROM Students").empty:
        return
    students = [
        ("Aarav Sharma","24BCA10001","24BCA1-A",3,"aarav@example.com"),
        ("Diya Verma","24BCA10002","24BCA1-A",3,"diya@example.com"),
        ("Kabir Singh","24BCA10003","24BCA1-A",3,"kabir@example.com"),
        ("Meera Kapoor","24BCA10004","24BCA1-A",3,"meera@example.com"),
        ("Rohan Gupta","24BCA10005","24BCA1-A",3,"rohan@example.com"),
        ("Ananya Patel","24BCA10006","24BCA1-A",3,"ananya@example.com"),
        ("Vivaan Das","24BCA10007","24BCA1-A",3,"vivaan@example.com"),
        ("Ishita Rao","24BCA10008","24BCA1-A",3,"ishita@example.com"),
        ("Arjun Mehta","24BCA10009","24BCA1-A",3,"arjun@example.com"),
        ("Sara Khan","24BCA10010","24BCA1-A",3,"sara@example.com"),
    ]
    for row in students:
        add_student(*row)
    subjects = [("Python Programming","24CAP301",100),("Database Management","24CAT302",100),
                ("Data Structures","24CAT303",100),("Computer Networks","24CAT304",100),
                ("Web Technology","24CAT305",100)]
    for row in subjects:
        add_subject(*row)
    rng = __import__("random").Random(21)
    sids = query_df("SELECT student_id FROM Students").student_id.tolist()
    subs = query_df("SELECT subject_id FROM Subjects").subject_id.tolist()
    for sid in sids:
        for sub in subs:
            internal = rng.randint(22, 48)
            external = rng.randint(15, 49)
            total = internal + external
            pct = total
            grade = "A+" if pct >= 90 else "A" if pct >= 80 else "B+" if pct >= 70 else "B" if pct >= 60 else "C" if pct >= 50 else "D" if pct >= 40 else "F"
            save_performance(sid, sub, 3, internal, external, grade, "Pass" if pct >= 40 else "Fail")
