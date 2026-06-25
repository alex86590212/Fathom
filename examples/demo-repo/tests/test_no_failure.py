"""Dishonest tests — no possible failure path (pattern: no_failure_path)."""


def test_always_passes():
    assert True


def test_literal_equality():
    assert 42 == 42
