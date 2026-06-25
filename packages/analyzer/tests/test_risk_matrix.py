"""Tests for risk matrix classification."""

from fathom.risk_matrix import RiskZone, classify


def test_critical_zone():
    assert classify(30, 30) == RiskZone.CRITICAL


def test_fragile_zone():
    assert classify(30, 70) == RiskZone.FRAGILE


def test_blind_spot_zone():
    assert classify(70, 30) == RiskZone.BLIND_SPOT


def test_healthy_zone():
    assert classify(70, 70) == RiskZone.HEALTHY
