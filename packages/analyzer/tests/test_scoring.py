"""Tests for honesty scoring."""

from fathom.test_honesty.scoring import (
    FINDING_HONESTY_CAP,
    TEST_HONESTY_THRESHOLD,
    honesty_score,
    is_low_honesty,
)


def test_perfect_score_no_findings():
    assert honesty_score([]) == 100.0
    assert not is_low_honesty(100.0, [])


def test_deductions_floor_at_zero():
    findings = [
        {"pattern": "internal_module_mock"},
        {"pattern": "mocked_coverage"},
        {"pattern": "tautological_assertion"},
        {"pattern": "no_failure_path"},
        {"pattern": "internal_module_mock"},
    ]
    assert honesty_score(findings) == 0.0


def test_single_serious_pattern_below_threshold():
    score = honesty_score([{"pattern": "internal_module_mock"}])
    assert score < TEST_HONESTY_THRESHOLD
    assert is_low_honesty(score, [{"pattern": "internal_module_mock"}])


def test_findings_cap_honesty_even_if_penalty_mild():
    # Even a pattern with a smaller penalty must not read as "high honesty".
    score = honesty_score([{"pattern": "unknown_pattern"}])
    assert score <= FINDING_HONESTY_CAP


def test_no_failure_path_two_findings():
    findings = [{"pattern": "no_failure_path"}, {"pattern": "no_failure_path"}]
    assert honesty_score(findings) == 30.0
