"""PDF and Excel export utilities."""
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def export_excel(df, filename="class_performance.xlsx"):
    path = REPORT_DIR / filename
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Performance")
        if not df.empty:
            df.groupby("subject_name").percentage.mean().round(2).reset_index().to_excel(
                writer, index=False, sheet_name="Subject Summary")
    return path

def export_pdf(title, df, filename="performance_report.pdf"):
    path = REPORT_DIR / filename
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=24,leftMargin=24)
    story = [Paragraph(title, styles["Title"]), Spacer(1,12),
             Paragraph("Student Performance Analysis System | Amber Saxena | UID: 24BCA10021", styles["Normal"]),
             Spacer(1,12)]
    if df.empty:
        story.append(Paragraph("No performance records are available.", styles["BodyText"]))
    else:
        view = df.copy()
        for c in view.select_dtypes(include="number").columns:
            view[c] = view[c].round(2)
        data = [list(view.columns)] + view.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172554")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#64748b")),
            ("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#eff6ff")]),
            ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)
        ]))
        story.append(table)
    doc.build(story)
    return path
