"""
Scoring and letter-grade computation.
Starts at 100, deducts penalties from failed/warned checks,
then maps the final score to a letter grade.
"""

GRADE_BANDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0,  "F"),
]


def compute_grade(check_results: list[dict]) -> dict:
    """
    Compute an overall score and letter grade from a list of check_result dicts.

    Args:
        check_results: list of dicts; each must have a 'score_impact' key (negative int = penalty).
    Returns:
        {"score": int (0–100), "grade": str (A–F)}
    """
    total_penalty = sum(abs(min(r.get("score_impact", 0), 0)) for r in check_results)
    score = max(0, 100 - total_penalty)

    grade = "F"
    for threshold, letter in GRADE_BANDS:
        if score >= threshold:
            grade = letter
            break

    return {"score": score, "grade": grade}
