from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"


def dataframe_excel(data: pd.DataFrame, sheet_name: str = "Report") -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buffer.getvalue()


def student_pdf(student: dict, marks: pd.DataFrame) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph("STUDENT PERFORMANCE REPORT", styles["Title"]), Paragraph("Chandigarh University • BCA • 24BCA1-A", styles["Normal"]), Spacer(1, 0.2 * inch)]
    story.append(Paragraph(f"<b>{student['name']}</b> | UID: {student['uid']} | Semester: {student['semester']}", styles["Heading2"]))
    story.append(Spacer(1, 0.15 * inch))
    rows = [["Subject", "Total", "Percentage", "Grade", "Result"]] + marks[["subject_name", "total_marks", "percentage", "grade", "result"]].values.tolist()
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("ALIGN", (1, 1), (-1, -1), "CENTER")]))
    story.extend([table, Spacer(1, 0.2 * inch), Paragraph(f"Generated on {datetime.now():%d %B %Y, %I:%M %p}", styles["Normal"]), Paragraph("Designed & Developed by Amber Saxena | BCA | Chandigarh University", styles["Normal"])])
    doc.build(story)
    return buffer.getvalue()
