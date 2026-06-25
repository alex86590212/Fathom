"""Tests for unified Fathom report."""

from pathlib import Path

from fathom.report import build_report, format_markdown

DEMO_TESTS = Path(__file__).resolve().parents[3] / "examples" / "demo-repo" / "tests"


def test_build_report_shape():
    report = build_report(DEMO_TESTS, use_git_origin=False)
    assert report.files_scanned >= 4
    assert report.files
    assert "findings" in report.to_dict()
    assert sum(report.summary.values()) == report.files_scanned


def test_format_markdown_contains_marker():
    report = build_report(DEMO_TESTS, use_git_origin=False)
    md = format_markdown(report)
    assert "<!-- fathom-report -->" in md
    assert "Fathom Risk Report" in md


def test_progress_callback():
    phases: list[str] = []
    build_report(DEMO_TESTS, use_git_origin=False, on_progress=phases.append)
    assert phases
