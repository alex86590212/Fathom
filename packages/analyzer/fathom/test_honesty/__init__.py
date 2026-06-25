"""Test honesty analysis — AST-based detection of dishonest test patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fathom.test_honesty.analyzers import analyze_file
from fathom.test_honesty.patterns import TestHonestyPattern


def analyze_directory(path: Path) -> dict[str, Any]:
    """Walk PATH for Python test files and run honesty analyzers."""
    findings: list[dict[str, Any]] = []
    test_files = _discover_test_files(path)

    for test_file in test_files:
        findings.extend(analyze_file(test_file))

    return {
        "path": str(path),
        "files_scanned": len(test_files),
        "findings": findings,
    }


def _discover_test_files(path: Path) -> list[Path]:
    """Find test_*.py and *_test.py files under path."""
    if path.is_file() and path.suffix == ".py":
        return [path]

    patterns = ("test_*.py", "*_test.py")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path.rglob(pattern))
    return sorted(set(files))
