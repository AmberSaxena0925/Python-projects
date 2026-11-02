"""Vercel entrypoint for the Student Performance Analysis API."""

from flask import Flask, jsonify

from student_performance_analysis import analysis
from student_performance_analysis import db


app = Flask(__name__)
db.initialize_database()


def performance_data():
    return db.query_df(
        """
        SELECT p.performance_id, s.student_id, s.name, s.uid, s.section,
               p.semester, sub.subject_name, sub.subject_code,
               p.internal_marks, p.external_marks, p.total_marks,
               p.percentage, p.grade, p.result
        FROM performance AS p
        JOIN students AS s ON p.student_id = s.student_id
        JOIN subjects AS sub ON p.subject_id = sub.subject_id
        ORDER BY s.name, p.semester, sub.subject_name
        """
    )


def summary_data(data):
    if data.empty:
        return {"average": 0.0, "highest": 0.0, "lowest": 0.0, "pass_rate": 0.0}
    return {
        "average": round(float(data["percentage"].mean()), 2),
        "highest": round(float(data["percentage"].max()), 2),
        "lowest": round(float(data["percentage"].min()), 2),
        "pass_rate": round(float(data["result"].eq("Pass").mean() * 100), 2),
    }


@app.get("/")
def home():
    data = performance_data()
    summary = summary_data(data)
    ranking = analysis.student_averages(data).head(10) if not data.empty else data
    rows = ranking.to_dict(orient="records")
    table = "".join(
        f"<tr><td>{index}</td><td>{row['name']}</td>"
        f"<td>{row['uid']}</td><td>{row['average_percentage']:.2f}%</td></tr>"
        for index, row in enumerate(rows, start=1)
    ) or '<tr><td colspan="4">No performance records yet.</td></tr>'
    students = int(db.query_df("SELECT COUNT(*) AS count FROM students").iloc[0]["count"])
    cards = "".join(
        f'<div class="card"><b>{label}</b><br>{value}</div>'
        for label, value in [
            ("Students", students),
            ("Average", f"{summary['average']}%"),
            ("Highest", f"{summary['highest']}%"),
            ("Lowest", f"{summary['lowest']}%"),
            ("Pass rate", f"{summary['pass_rate']}%"),
        ]
    )
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
<section class="cards">{cards}</section>
<h2>Top performers</h2><table><tr><th>Rank</th><th>Name</th><th>UID</th><th>Average</th></tr>{table}</table>
</main></body></html>"""


@app.get("/api/summary")
def summary():
    data = performance_data()
    result = summary_data(data)
    result["students"] = int(db.query_df("SELECT COUNT(*) AS count FROM students").iloc[0]["count"])
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
