"""Dishonest tests — mocked coverage (pattern: mocked_coverage with --coverage)."""

from unittest.mock import patch

from demo_app import multiply


@patch("demo_app.multiply")
def test_multiply_mocked(mock_mul):
    mock_mul.return_value = 20
    assert multiply(4, 5) == 20
