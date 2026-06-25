"""Risk matrix — combine comprehension and test honesty into zones."""

from __future__ import annotations

from enum import Enum


class RiskZone(Enum):
    CRITICAL = "critical"  # low comprehension + low test honesty
    FRAGILE = "fragile"  # low comprehension + high test honesty
    BLIND_SPOT = "blind_spot"  # high comprehension + low test honesty
    HEALTHY = "healthy"  # high comprehension + high test honesty


COMPREHENSION_THRESHOLD = 50.0
TEST_HONESTY_THRESHOLD = 50.0


def classify(comprehension_score: float, test_honesty_score: float) -> RiskZone:
    """Place a file in the 2×2 risk matrix."""
    low_comprehension = comprehension_score < COMPREHENSION_THRESHOLD
    low_honesty = test_honesty_score < TEST_HONESTY_THRESHOLD

    if low_comprehension and low_honesty:
        return RiskZone.CRITICAL
    if low_comprehension:
        return RiskZone.FRAGILE
    if low_honesty:
        return RiskZone.BLIND_SPOT
    return RiskZone.HEALTHY
