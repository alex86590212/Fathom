"""Tests for shared AST utilities."""

import ast

from fathom.test_honesty.ast_utils import extract_patch_targets, iter_patch_calls


def test_extract_patch_object_target():
    source = """
from unittest.mock import patch
import demo_app
patch.object(demo_app, "add")
"""
    tree = ast.parse(source)
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][-1]
    assert extract_patch_targets(call) == ["demo_app.add"]


def test_extract_patch_multiple_target():
    source = """
from unittest.mock import patch
patch.multiple("demo_app", add=1)
"""
    tree = ast.parse(source)
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][-1]
    assert extract_patch_targets(call) == ["demo_app"]


def test_iter_patch_calls_deduplicates_same_line():
    source = """
from unittest.mock import patch
from demo_app import add
with patch("demo_app.add"):
    patch("demo_app.add")
"""
    tree = ast.parse(source)
    hits = iter_patch_calls(tree)
    assert len(hits) == 2
    assert hits[0][1] == hits[1][1] == "demo_app.add"
