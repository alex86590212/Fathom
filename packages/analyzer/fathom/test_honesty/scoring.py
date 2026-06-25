"""Per-file test honesty scoring from findings."""

from __future__ import annotations

from typing import Any

# Penalties chosen so a single serious pattern drops below TEST_HONESTY_THRESHOLD (50).
PATTERN_PENALTIES: dict[str, int] = {
    "internal_module_mock": 55,
    "tautological_assertion": 50,
    "no_failure_path": 35,
    "mocked_coverage": 60,
}

# Any finding means the file is not "high honesty" on the risk matrix.
FINDING_HONESTY_CAP = 49.0
TEST_HONESTY_THRESHOLD = 50.0


def honesty_score(findings: list[dict[str, Any]]) -> float:
    """Compute 0–100 honesty score; 100 = no findings.

  Files with findings are capped below the honesty threshold so zones
  reflect detected dishonest patterns, not just numeric deductions.
    """
    if not findings:
        return 100.0

    score = 100.0
    for finding in findings:
        score -= PATTERN_PENALTIES.get(finding.get("pattern", ""), 25)
    score = max(0.0, score)
    return min(score, FINDING_HONESTY_CAP)


def is_low_honesty(score: float, findings: list[dict[str, Any]]) -> bool:
    """True when honesty score or findings place the file on the low-honesty axis."""
    return bool(findings) or score < TEST_HONESTY_THRESHOLD
