"""Tests for CLI display rendering."""

from fathom.display import print_report
from rich.console import Console


def test_print_report_renders_matrix_and_findings():
    console = Console(width=120, record=True)
    report = {
        "path": "tests/",
        "files_scanned": 2,
        "summary": {"critical": 1, "fragile": 0, "blind_spot": 0, "healthy": 1},
        "files": [
            {
                "path": "/proj/tests/test_bad.py",
                "risk_zone": "critical",
                "test_honesty_score": 45,
                "comprehension_score": 5,
                "findings": [
                    {
                        "file": "/proj/tests/test_bad.py",
                        "line": 8,
                        "pattern": "internal_module_mock",
                        "message": "Patching internal module",
                    }
                ],
            },
            {
                "path": "/proj/tests/test_ok.py",
                "risk_zone": "healthy",
                "test_honesty_score": 100,
                "comprehension_score": 70,
                "findings": [],
            },
        ],
        "findings": [
            {
                "file": "/proj/tests/test_bad.py",
                "line": 8,
                "pattern": "internal_module_mock",
                "message": "Patching internal module",
            }
        ],
    }
    print_report(console, report, path="tests/")
    out = console.export_text()
    assert "Risk matrix" in out
    assert "Critical" in out
    assert "test_bad.py" in out
    assert "Internal mock" in out
