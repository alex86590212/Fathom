"""Dishonest tests — tautological assertions (pattern: tautological_assertion)."""

from unittest.mock import MagicMock


def test_tautological():
    mock = MagicMock()
    mock.return_value = 42
    assert mock() == mock.return_value  # always true
