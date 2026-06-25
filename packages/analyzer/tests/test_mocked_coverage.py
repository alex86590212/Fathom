"""Tests for mocked coverage pattern."""

from pathlib import Path

from fathom.test_honesty.analyzers import analyze_file
from fathom.test_honesty.coverage_data import load_coverage

FIXTURES = Path(__file__).parent / "fixtures"
DEMO = Path(__file__).resolve().parents[3] / "examples" / "demo-repo" / "tests"


def test_mocked_coverage_with_coverage_json():
    coverage = load_coverage(FIXTURES / "coverage.json")
    findings = analyze_file(DEMO / "test_mocked_coverage.py", coverage_data=coverage)
    patterns = {f["pattern"] for f in findings}
    assert "mocked_coverage" in patterns


def test_mocked_coverage_without_coverage_data():
    findings = analyze_file(DEMO / "test_mocked_coverage.py", coverage_data=None)
    patterns = {f["pattern"] for f in findings}
    assert "mocked_coverage" not in patterns
