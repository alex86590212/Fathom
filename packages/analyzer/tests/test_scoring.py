"""Tests for honesty scoring."""

from fathom.test_honesty.scoring import honesty_score


def test_perfect_score_no_findings():
    assert honesty_score([]) == 100.0


def test_deductions_floor_at_zero():
    findings = [
        {"pattern": "internal_module_mock"},
        {"pattern": "mocked_coverage"},
        {"pattern": "tautological_assertion"},
        {"pattern": "no_failure_path"},
        {"pattern": "internal_module_mock"},
    ]
    assert honesty_score(findings) == 0.0


def test_single_pattern_penalty():
    assert honesty_score([{"pattern": "no_failure_path"}]) == 85.0
