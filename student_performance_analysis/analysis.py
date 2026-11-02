from __future__ import annotations

import numpy as np
import pandas as pd


def student_averages(performance: pd.DataFrame) -> pd.DataFrame:
    return performance.groupby(["student_id", "name", "uid"], as_index=False).agg(average_percentage=("percentage", "mean"), subjects=("subject_name", "count"), passed=("result", lambda values: (values == "Pass").sum())).sort_values("average_percentage", ascending=False)


def subject_averages(performance: pd.DataFrame) -> pd.DataFrame:
    return performance.groupby("subject_name", as_index=False).agg(average_percentage=("percentage", "mean"), pass_rate=("result", lambda values: (values == "Pass").mean() * 100), attempts=("percentage", "count")).sort_values("average_percentage", ascending=False)


def grade_distribution(performance: pd.DataFrame) -> pd.DataFrame:
    return performance["grade"].value_counts().rename_axis("grade").reset_index(name="count")


def improvement_candidates(averages: pd.DataFrame, threshold: float = 60) -> pd.DataFrame:
    return averages[averages["average_percentage"] < threshold].copy()


def predict_next_score(semester_scores: pd.Series | list[float]) -> float | None:
    values = np.asarray(semester_scores, dtype=float)
    if values.size == 0:
        return None
    if values.size == 1:
        return round(float(values[0]), 2)
    prediction = np.polyval(np.polyfit(np.arange(1, values.size + 1), values, 1), values.size + 1)
    return round(float(np.clip(prediction, 0, 100)), 2)


def recommendation(weak_subjects: list[str]) -> str:
    if not weak_subjects:
        return "Excellent balance across subjects. Maintain your study routine and mentor peers."
    return "Prioritise " + ", ".join(weak_subjects[:3]) + ". Schedule two focused practice sessions and one revision quiz each week."
