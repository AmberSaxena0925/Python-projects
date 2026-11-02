"""Vercel entrypoint for the Student Performance Analysis System.

The original Streamlit interface is preserved in ``streamlit_app.py``. Vercel
loads this module as a WSGI application, so the exported ``app`` object is the
Flask application below.
"""

from flask import Flask, jsonify

import analysis
import database as db


app = Flask(__name__)
db.init_db()


def performance_data():
    return db.query_df(
        """SELECT p.performance_id, s.student_id, s.name, s.uid, s.section,
        p.semester, sub.subject_name, sub.subject_code, p.internal_marks,
        p.external_marks, p.total_marks, p.percentage, p.grade, p.result
        FROM Performance p
        JOIN Students s ON p.student_id = s.student_id
        JOIN Subjects sub ON p.subject_id = sub.subject_id
        ORDER BY s.name, p.semester, sub.subject_name"""
    )


@app.get("/")
def home():
    data = performance_data()
    summary = analysis.class_summary(data)
    ranking = analysis.student_ranking(data).head(10)
    rows = ranking.to_dict(orient="records")
    table = "".join(
        f"<tr><td>{row['rank']}</td><td>{row['name']}</td>"
        f"<td>{row['uid']}</td><td>{row['average']:.2f}%</td></tr>"
        for row in rows
    ) or '<tr><td colspan="4">No performance records yet.</td></tr>'
    return f"""<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Performance Analysis</title>
<style>body{{font:16px system-ui;margin:0;background:#080d1b;color:#e5e7eb}}
main{{max-width:1000px;margin:auto;padding:32px}}h1{{color:#93c5fd}}
.cards{{display:flex;flex-wrap:wrap;gap:12px}}.card{{background:#111c35;
padding:18px;border:1px solid #293b5d;border-radius:12px;min-width:140px}}
table{{width:100%;margin-top:24px;border-collapse:collapse;background:#111827}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #263858}}
small{{color:#9caecb}}</style></head><body><main>
<h1>Student Performance Analysis</h1><small>Vercel Flask deployment</small>
<section class="cards">{''.join(f'<div class="card"><b>{label}</b><br>{value}</div>' for label, value in [
('Students', len(db.query_df('SELECT student_id FROM Students'))),
('Average', f"{summary['average']}%"), ('Highest', f"{summary['highest']}%"),
('Lowest', f"{summary['lowest']}%"), ('Pass rate', f"{summary['pass_rate']}%")])}</section>
<h2>Top performers</h2><table><tr><th>Rank</th><th>Name</th><th>UID</th><th>Average</th></tr>{table}</table>
</main></body></html>"""


@app.get("/api/summary")
def summary():
    data = performance_data()
    result = analysis.class_summary(data)
    result["students"] = int(db.query_df("SELECT COUNT(*) AS count FROM Students").iloc[0]["count"])
    return jsonify(result)


@app.get("/api/performance")
def performance():
    return jsonify(performance_data().to_dict(orient="records"))


@app.post("/api/demo")
def demo():
    db.seed_demo_data()
    return jsonify({"status": "ok", "message": "Demo data is ready."})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
