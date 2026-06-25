"""Test honesty analysis — AST-based detection of dishonest test patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def analyze_directory(
    path: Path,
    coverage_path: Path | None = None,
    use_git_origin: bool = True,
    on_progress=None,
) -> dict[str, Any]:
    """Walk PATH for Python test files and return a full Fathom report dict."""
    from fathom.report import build_report

    report = build_report(
        path,
        coverage_path=coverage_path,
        use_git_origin=use_git_origin,
        on_progress=on_progress,
    )
    return report.to_dict()


__all__ = ["analyze_directory"]
