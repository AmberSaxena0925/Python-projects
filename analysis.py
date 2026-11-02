"""Academic calculations, ranking, insights and simple trend prediction."""
import numpy as np
import pandas as pd

DEFAULT_SCALE = [(90,"A+"),(80,"A"),(70,"B+"),(60,"B"),(50,"C"),(40,"D"),(0,"F")]

def grade_for(pct, scale=None):
    for floor, grade in (scale or DEFAULT_SCALE):
        if pct >= floor:
            return grade
    return "F"

def performance_frame(df):
    if df.empty:
        return df.copy()
    out = df.copy()
    out["percentage"] = pd.to_numeric(out["percentage"], errors="coerce").fillna(0)
    return out

def class_summary(df):
    if df.empty:
        return {"records":0,"average":0,"highest":0,"lowest":0,"pass_rate":0}
    p = performance_frame(df)
    return {"records":len(p), "average":round(p.percentage.mean(),2),
            "highest":round(p.percentage.max(),2), "lowest":round(p.percentage.min(),2),
            "pass_rate":round((p.result == "Pass").mean()*100,2)}

def student_ranking(df):
    if df.empty:
        return pd.DataFrame(columns=["uid","name","average","subjects","rank"])
    x = df.groupby(["student_id","uid","name"],as_index=False).agg(
        average=("percentage","mean"), subjects=("subject_name","nunique"))
    x = x.sort_values(["average","name"],ascending=[False,True]).reset_index(drop=True)
    x["average"] = x.average.round(2)
    x.insert(0,"rank",range(1,len(x)+1))
    return x

def subject_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["subject_name","average","pass_rate","attempts"])
    return (df.groupby("subject_name",as_index=False)
            .agg(average=("percentage","mean"),
                 pass_rate=("result",lambda s:(s=="Pass").mean()*100),
                 attempts=("percentage","count"))
            .round(2).sort_values("average"))

def student_insights(student_df, threshold=60):
    if student_df.empty:
        return ["No marks have been recorded for this student yet."]
    avg = student_df.percentage.mean()
    weak = student_df[student_df.percentage < threshold].subject_name.tolist()
    strong = student_df[student_df.percentage >= 80].subject_name.tolist()
    notes = [f"Overall average: {avg:.1f}%."]
    if weak:
        notes.append("Needs improvement in: " + ", ".join(weak) + ". Create a weekly revision plan and practise topic-wise questions.")
    else:
        notes.append("No subject is currently below the improvement threshold.")
    if strong:
        notes.append("Strong subjects: " + ", ".join(strong) + ". Maintain this performance through regular practice.")
    if avg < 40:
        notes.append("Priority alert: schedule a faculty check-in and a focused recovery plan.")
    elif avg >= 85:
        notes.append("Excellent performance. Consider advanced assignments or peer mentoring.")
    return notes

def predict_next_score(history):
    """Simple least-squares trend estimate; returns None when fewer than 2 semesters exist."""
    if history is None or len(history) < 2:
        return None
    h = history.sort_values("semester")
    x = h.semester.to_numpy(dtype=float)
    y = h.percentage.to_numpy(dtype=float)
    if len(np.unique(x)) < 2:
        return None
    slope, intercept = np.polyfit(x,y,1)
    return float(np.clip(slope*(x.max()+1)+intercept,0,100))
