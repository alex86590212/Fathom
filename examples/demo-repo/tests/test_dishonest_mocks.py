"""Dishonest tests — internal module mocking (pattern: internal_module_mock)."""

from unittest.mock import patch

from demo_app import add


@patch("demo_app.add")
def test_add_with_mock(mock_add):
    mock_add.return_value = 5
    result = add(2, 3)
    assert result == 5  # tests the mock, not the function
