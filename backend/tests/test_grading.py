"""
Tests for the scoring and grading model.
"""
from engine.grading import compute_grade


def test_no_penalties_gives_perfect_score():
    result = compute_grade([])
    assert result["score"] == 100
    assert result["grade"] == "A"


def test_small_penalty_stays_in_a_band():
    result = compute_grade([{"score_impact": -5}])
    assert result["score"] == 95
    assert result["grade"] == "A"


def test_b_band():
    result = compute_grade([{"score_impact": -15}])
    assert result["score"] == 85
    assert result["grade"] == "B"


def test_c_band():
    result = compute_grade([{"score_impact": -25}])
    assert result["score"] == 75
    assert result["grade"] == "C"


def test_d_band():
    result = compute_grade([{"score_impact": -35}])
    assert result["score"] == 65
    assert result["grade"] == "D"


def test_f_band():
    result = compute_grade([{"score_impact": -50}])
    assert result["score"] == 50
    assert result["grade"] == "F"


def test_score_never_goes_below_zero():
    result = compute_grade([{"score_impact": -9999}])
    assert result["score"] == 0
    assert result["grade"] == "F"


def test_positive_score_impact_is_ignored():
    # Only penalties count; positive values should have no effect
    result = compute_grade([{"score_impact": 50}])
    assert result["score"] == 100


def test_multiple_checks_accumulate():
    checks = [{"score_impact": -10}, {"score_impact": -10}, {"score_impact": -5}]
    result = compute_grade(checks)
    assert result["score"] == 75
    assert result["grade"] == "C"
