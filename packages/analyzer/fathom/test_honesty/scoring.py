"""Per-file test honesty scoring from findings."""

from __future__ import annotations

from typing import Any

PATTERN_PENALTIES: dict[str, int] = {
    "internal_module_mock": 25,
    "tautological_assertion": 20,
    "no_failure_path": 15,
    "mocked_coverage": 30,
}


def honesty_score(findings: list[dict[str, Any]]) -> float:
    """Compute 0–100 honesty score; 100 = no findings."""
    score = 100.0
    for finding in findings:
        score -= PATTERN_PENALTIES.get(finding.get("pattern", ""), 10)
    return max(0.0, score)
