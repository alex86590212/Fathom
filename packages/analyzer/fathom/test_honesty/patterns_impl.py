"""Concrete test honesty pattern implementations."""

from __future__ import annotations

import ast

from fathom.test_honesty.patterns import PatternHit, TestHonestyPattern

# Known third-party / infrastructure roots — patching these is usually legitimate.
_EXTERNAL_ROOTS = frozenset(
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
    }
)


def _line(node: ast.AST) -> int:
    return getattr(node, "lineno", 1)


def _is_patch_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False

    func = node.func
    if isinstance(func, ast.Name) and func.id == "patch":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "patch":
        return True
    return False


def _patch_target(node: ast.Call) -> str | None:
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def _local_modules(tree: ast.Module) -> set[str]:
    """Top-level modules imported in this test file (project code proxy)."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
    return modules


def _is_internal_patch(target: str, local_modules: set[str]) -> bool:
    root = target.split(".")[0]
    if root in _EXTERNAL_ROOTS:
        return False
    return root in local_modules


def _is_mock_return_value_tautology(node: ast.AST) -> bool:
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


def _is_literal_tautology(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and node.value is True:
        return True

    if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
        if len(node.comparators) == 1:
            return ast.dump(node.left, annotate_fields=False) == ast.dump(
                node.comparators[0], annotate_fields=False
            )
    return False


class InternalModuleMockPattern(TestHonestyPattern):
    """Mocking your own internal modules (not external APIs/DBs)."""

    pattern_id = "internal_module_mock"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        local = _local_modules(tree)
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not _is_patch_call(node):
                continue

            target = _patch_target(node)
            if not target or not _is_internal_patch(target, local):
                continue

            hits.append(
                PatternHit(
                    line=_line(node),
                    pattern_id=self.pattern_id,
                    message=(
                        f'Patching internal module "{target}" — '
                        "tests the mock, not real behavior"
                    ),
                )
            )

        return hits


class TautologicalAssertionPattern(TestHonestyPattern):
    """Assertions against mock return values — expect(mockFn()).toBe(mockFn())."""

    pattern_id = "tautological_assertion"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue

            if _is_mock_return_value_tautology(node.test):
                hits.append(
                    PatternHit(
                        line=_line(node),
                        pattern_id=self.pattern_id,
                        message="Assertion compares mock() to mock.return_value — always true",
                    )
                )
                continue

            if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1:
                if isinstance(node.test.ops[0], ast.Eq) and len(node.test.comparators) == 1:
                    left, right = node.test.left, node.test.comparators[0]
                    # Literal equality (42 == 42) is no_failure_path, not tautological_assertion.
                    if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                        continue
                    if ast.dump(left, annotate_fields=False) == ast.dump(
                        right, annotate_fields=False
                    ):
                        hits.append(
                            PatternHit(
                                line=_line(node),
                                pattern_id=self.pattern_id,
                                message="Assertion compares a value to itself — tautological",
                            )
                        )

        return hits


class NoFailurePathPattern(TestHonestyPattern):
    """Tests with no possible failure path."""

    pattern_id = "no_failure_path"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue

            if not _is_literal_tautology(node.test):
                continue

            # Skip if already covered by tautological_assertion (mock-specific).
            if _is_mock_return_value_tautology(node.test):
                continue

            hits.append(
                PatternHit(
                    line=_line(node),
                    pattern_id=self.pattern_id,
                    message="Assertion cannot fail — no real behavior is verified",
                )
            )

        return hits


class MockedCoveragePattern(TestHonestyPattern):
    """100% coverage via mocked paths — line runs but behavior untested."""

    pattern_id = "mocked_coverage"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        if not self.coverage_data:
            return []

        from fathom.test_honesty.coverage_data import module_has_executed_lines

        local = _local_modules(tree)
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not _is_patch_call(node):
                continue
            target = _patch_target(node)
            if not target or not _is_internal_patch(target, local):
                continue
            if module_has_executed_lines(self.coverage_data, target.split(".")[0]):
                hits.append(
                    PatternHit(
                        line=_line(node),
                        pattern_id=self.pattern_id,
                        message=(
                            f'Coverage shows "{target}" lines executed while test mocks '
                            "internal code — real behavior may be untested"
                        ),
                    )
                )

        return hits
