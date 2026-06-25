"""Tests for test honesty pattern detectors."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from fathom.test_honesty.patterns_impl import (
    InternalModuleMockPattern,
    NoFailurePathPattern,
    TautologicalAssertionPattern,
)

DEMO_TESTS = Path(__file__).resolve().parents[3] / "examples" / "demo-repo" / "tests"


def _parse(path: Path) -> tuple[ast.Module, str]:
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path)), source


def test_internal_module_mock_finds_patch_decorator():
    tree, source = _parse(DEMO_TESTS / "test_dishonest_mocks.py")
    hits = InternalModuleMockPattern().detect(tree, source)

    assert len(hits) == 1
    assert hits[0].pattern_id == "internal_module_mock"
    assert "demo_app.add" in hits[0].message


def test_internal_module_mock_ignores_external_patch():
    source = """
import requests
from unittest.mock import patch

@patch("requests.get")
def test_external(mock_get):
    mock_get.return_value = object()
    assert mock_get is not None
"""
    tree = ast.parse(source)
    hits = InternalModuleMockPattern().detect(tree, source)
    assert hits == []


def test_internal_module_mock_finds_mocker_patch():
    source = """
from demo_app import add

def test_with_mocker(mocker):
    mocker.patch("demo_app.add", return_value=5)
    assert add(2, 3) == 5
"""
    tree = ast.parse(source)
    hits = InternalModuleMockPattern().detect(tree, source)

    assert len(hits) == 1
    assert hits[0].pattern_id == "internal_module_mock"


def test_tautological_assertion_finds_mock_return_value():
    tree, source = _parse(DEMO_TESTS / "test_tautological.py")
    hits = TautologicalAssertionPattern().detect(tree, source)

    assert len(hits) == 1
    assert hits[0].pattern_id == "tautological_assertion"


def test_tautological_assertion_finds_self_comparison():
    source = """
def test_self_eq():
    x = 1
    assert x == x
"""
    tree = ast.parse(source)
    hits = TautologicalAssertionPattern().detect(tree, source)

    assert len(hits) == 1


def test_no_failure_path_finds_literal_assertions():
    tree, source = _parse(DEMO_TESTS / "test_no_failure.py")
    hits = NoFailurePathPattern().detect(tree, source)

    assert len(hits) == 2
    assert all(h.pattern_id == "no_failure_path" for h in hits)


def test_honest_tests_have_no_findings():
    tree, source = _parse(DEMO_TESTS / "test_honest.py")

    assert InternalModuleMockPattern().detect(tree, source) == []
    assert TautologicalAssertionPattern().detect(tree, source) == []
    assert NoFailurePathPattern().detect(tree, source) == []


@pytest.mark.parametrize(
    "filename,expected_patterns",
    [
        ("test_dishonest_mocks.py", {"internal_module_mock"}),
        ("test_tautological.py", {"tautological_assertion"}),
        ("test_no_failure.py", {"no_failure_path"}),
        ("test_honest.py", set()),
    ],
)
def test_demo_repo_files(filename: str, expected_patterns: set[str]):
    from fathom.test_honesty.analyzers import analyze_file

    findings = analyze_file(DEMO_TESTS / filename)
    patterns = {f["pattern"] for f in findings}
    assert patterns == expected_patterns
