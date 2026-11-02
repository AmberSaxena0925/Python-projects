from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "student_performance.db"

DEFAULT_GRADE_SCALE = ((90, "A+"), (80, "A"), (70, "B+"), (60, "B"), (50, "C"), (40, "D"), (0, "F"))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def calculate_grade(percentage: float, scale: Iterable[tuple[float, str]] = DEFAULT_GRADE_SCALE) -> str:
    for threshold, grade in sorted(scale, reverse=True):
        if percentage >= threshold:
            return grade
    return "F"


def initialize_database() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                uid TEXT NOT NULL UNIQUE,
                section TEXT NOT NULL,
                semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
                email TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_code TEXT NOT NULL UNIQUE,
                maximum_marks REAL NOT NULL DEFAULT 100 CHECK (maximum_marks > 0)
            );
            CREATE TABLE IF NOT EXISTS performance (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
                semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
                internal_marks REAL NOT NULL CHECK (internal_marks >= 0),
                external_marks REAL NOT NULL CHECK (external_marks >= 0),
                total_marks REAL NOT NULL,
                percentage REAL NOT NULL,
                grade TEXT NOT NULL,
                result TEXT NOT NULL CHECK (result IN ('Pass', 'Fail')),
                UNIQUE(student_id, subject_id, semester)
            );
            """
        )


def seed_demo_data() -> None:
    initialize_database()
    students = [
        ("Aarav Sharma", "24BCA10001", "24BCA1-A", 4, "aarav.sharma@example.com"),
        ("Meera Kapoor", "24BCA10002", "24BCA1-A", 4, "meera.kapoor@example.com"),
        ("Rohan Verma", "24BCA10003", "24BCA1-A", 4, "rohan.verma@example.com"),
        ("Ananya Singh", "24BCA10004", "24BCA1-A", 4, "ananya.singh@example.com"),
        ("Kabir Malhotra", "24BCA10005", "24BCA1-A", 4, "kabir.malhotra@example.com"),
        ("Ishita Jain", "24BCA10006", "24BCA1-A", 4, "ishita.jain@example.com"),
    ]
    subjects = [("Python Programming", "BCA401", 100), ("Database Systems", "BCA402", 100), ("Data Analytics", "BCA403", 100), ("Web Technology", "BCA404", 100), ("Computer Networks", "BCA405", 100)]
    with get_connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] > 0:
            return
        conn.executemany("INSERT INTO students(name, uid, section, semester, email) VALUES (?, ?, ?, ?, ?)", students)
        conn.executemany("INSERT INTO subjects(subject_name, subject_code, maximum_marks) VALUES (?, ?, ?)", subjects)
        student_ids = [row[0] for row in conn.execute("SELECT student_id FROM students ORDER BY student_id")]
        subject_ids = [row[0] for row in conn.execute("SELECT subject_id FROM subjects ORDER BY subject_id")]
        patterns = [[86, 91, 78, 88, 82], [94, 89, 92, 90, 87], [64, 71, 58, 69, 62], [76, 83, 81, 79, 74], [42, 55, 49, 61, 47], [88, 72, 84, 80, 90]]
        for student_id, marks in zip(student_ids, patterns):
            for subject_id, total in zip(subject_ids, marks):
                internal, external = round(total * 0.4, 1), round(total * 0.6, 1)
                grade = calculate_grade(total)
                conn.execute("INSERT INTO performance(student_id, subject_id, semester, internal_marks, external_marks, total_marks, percentage, grade, result) VALUES (?, ?, 4, ?, ?, ?, ?, ?, ?)", (student_id, subject_id, internal, external, total, total, grade, "Pass" if total >= 40 else "Fail"))


def query_df(query: str, params: tuple[Any, ...] = ()):
    import pandas as pd
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    with get_connection() as conn:
        conn.execute(query, params)


def add_student(name: str, uid: str, section: str, semester: int, email: str) -> None:
    execute("INSERT INTO students(name, uid, section, semester, email) VALUES (?, ?, ?, ?, ?)", (name.strip(), uid.strip(), section.strip(), semester, email.strip().lower()))


def save_performance(student_id: int, subject_id: int, semester: int, internal: float, external: float) -> None:
    maximum = query_df("SELECT maximum_marks FROM subjects WHERE subject_id = ?", (subject_id,)).iloc[0, 0]
    total = internal + external
    percentage = round(total / maximum * 100, 2)
    execute("INSERT INTO performance(student_id, subject_id, semester, internal_marks, external_marks, total_marks, percentage, grade, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(student_id, subject_id, semester) DO UPDATE SET internal_marks=excluded.internal_marks, external_marks=excluded.external_marks, total_marks=excluded.total_marks, percentage=excluded.percentage, grade=excluded.grade, result=excluded.result", (student_id, subject_id, semester, internal, external, total, percentage, calculate_grade(percentage), "Pass" if percentage >= 40 else "Fail"))
