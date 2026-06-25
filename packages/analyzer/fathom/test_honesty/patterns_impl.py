"""Concrete test honesty pattern implementations."""

from __future__ import annotations

import ast

from fathom.test_honesty.ast_utils import (
    is_internal_target,
    is_literal_tautology,
    is_mock_return_value_tautology,
    is_self_comparison,
    iter_patch_calls,
    line_no,
    local_modules,
)
from fathom.test_honesty.patterns import PatternHit, TestHonestyPattern


class InternalModuleMockPattern(TestHonestyPattern):
    """Mocking your own internal modules (not external APIs/DBs)."""

    pattern_id = "internal_module_mock"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        local = local_modules(tree)
        hits: list[PatternHit] = []

        for line, target in iter_patch_calls(tree):
            if not is_internal_target(target, local):
                continue
            hits.append(
                PatternHit(
                    line=line,
                    pattern_id=self.pattern_id,
                    message=(
                        f'Patching internal module "{target}" — '
                        "tests the mock, not real behavior"
                    ),
                )
            )

        return hits


class TautologicalAssertionPattern(TestHonestyPattern):
    """Assertions that cannot meaningfully fail."""

    pattern_id = "tautological_assertion"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue

            if is_mock_return_value_tautology(node.test):
                hits.append(
                    PatternHit(
                        line=line_no(node),
                        pattern_id=self.pattern_id,
                        message="Assertion compares mock() to mock.return_value — always true",
                    )
                )
                continue

            if isinstance(node.test, ast.Compare) and is_self_comparison(node.test):
                hits.append(
                    PatternHit(
                        line=line_no(node),
                        pattern_id=self.pattern_id,
                        message="Assertion compares a value to itself — tautological",
                    )
                )

        return hits


# Keep test import compatibility
_is_mock_return_value_tautology = is_mock_return_value_tautology
_is_literal_tautology = is_literal_tautology


class NoFailurePathPattern(TestHonestyPattern):
    """Tests with no possible failure path."""

    pattern_id = "no_failure_path"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        hits: list[PatternHit] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue

            if not is_literal_tautology(node.test):
                continue

            if is_mock_return_value_tautology(node.test):
                continue

            hits.append(
                PatternHit(
                    line=line_no(node),
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

        local = local_modules(tree)
        hits: list[PatternHit] = []

        for line, target in iter_patch_calls(tree):
            if not is_internal_target(target, local):
                continue
            root = target.split(".")[0]
            if module_has_executed_lines(self.coverage_data, root):
                hits.append(
                    PatternHit(
                        line=line,
                        pattern_id=self.pattern_id,
                        message=(
                            f'Coverage shows "{target}" lines executed while test mocks '
                            "internal code — real behavior may be untested"
                        ),
                    )
                )

        return hits
