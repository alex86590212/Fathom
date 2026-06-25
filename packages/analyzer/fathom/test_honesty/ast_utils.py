"""Shared AST helpers for test-honesty detection — single-pass friendly."""

from __future__ import annotations

import ast

# Infrastructure / third-party roots — patching these is usually legitimate.
EXTERNAL_ROOTS: frozenset[str] = frozenset(
    {
        "requests",
        "httpx",
        "urllib3",
        "boto3",
        "botocore",
        "sqlalchemy",
        "redis",
        "celery",
        "stripe",
        "openai",
        "anthropic",
        "aiohttp",
        "psycopg2",
        "pymongo",
        "mysql",
        "elasticsearch",
        "kubernetes",
        "grpc",
        "socket",
        "subprocess",
        "os",
        "sys",
        "pathlib",
        "tempfile",
        "shutil",
        "json",
        "logging",
        "time",
        "datetime",
        "email",
        "smtplib",
    }
)


def line_no(node: ast.AST) -> int:
    return getattr(node, "lineno", 1)


def local_modules(tree: ast.Module) -> set[str]:
    """Top-level modules imported in this test file (proxy for project code)."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
    return modules


def is_external_root(root: str) -> bool:
    return root in EXTERNAL_ROOTS


def is_internal_target(target: str, local: set[str]) -> bool:
    root = target.split(".")[0]
    if is_external_root(root):
        return False
    return root in local


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        if base:
            return f"{base}.{node.attr}"
    return None


def _patch_callee(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name) and func.id == "patch":
        return "patch"
    if isinstance(func, ast.Attribute) and func.attr in ("patch", "object", "multiple"):
        return func.attr
    return None


def extract_patch_targets(node: ast.Call) -> list[str]:
    """Return module paths being patched, if recognizable."""
    kind = _patch_callee(node)
    if kind is None or not node.args:
        return []

    if kind == "patch":
        target = _dotted_name(node.args[0])
        return [target] if target else []

    if kind == "object":
        if len(node.args) < 2:
            return []
        base = _dotted_name(node.args[0])
        attr = node.args[1]
        if not base or not isinstance(attr, ast.Constant) or not isinstance(attr.value, str):
            return []
        return [f"{base}.{attr.value}"]

    if kind == "multiple":
        target = _dotted_name(node.args[0])
        return [target] if target else []

    return []


def iter_patch_calls(tree: ast.Module) -> list[tuple[int, str]]:
    """All (line, target) pairs from patch-like calls in the tree."""
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for target in extract_patch_targets(node):
            hits.append((line_no(node), target))
    return hits


def is_mock_return_value_tautology(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare):
        return False
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        return False
    if len(node.comparators) != 1:
        return False

    left, right = node.left, node.comparators[0]
    if isinstance(left, ast.Call) and isinstance(left.func, ast.Name):
        if isinstance(right, ast.Attribute) and isinstance(right.value, ast.Name):
            return left.func.id == right.value.id and right.attr == "return_value"
    return False


def is_literal_tautology(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and node.value is True:
        return True

    if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
        if len(node.comparators) == 1:
            left, right = node.left, node.comparators[0]
            if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                return True
    return False


def is_self_comparison(node: ast.Compare) -> bool:
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        return False
    if len(node.comparators) != 1:
        return False
    left, right = node.left, node.comparators[0]
    if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
        return False
    return ast.dump(left, annotate_fields=False) == ast.dump(right, annotate_fields=False)
