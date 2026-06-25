"""AST analyzers for dishonest test anti-patterns."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from fathom.test_honesty.patterns import TestHonestyPattern


def analyze_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse a Python test file and return findings for each detected pattern."""
    source = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []

    findings: list[dict[str, Any]] = []

    for pattern_cls in TestHonestyPattern.registry():
        pattern = pattern_cls()
        for hit in pattern.detect(tree, source):
            findings.append(
                {
                    "file": str(file_path),
                    "line": hit.line,
                    "pattern": hit.pattern_id,
                    "message": hit.message,
                    "severity": hit.severity,
                }
            )

    return findings
