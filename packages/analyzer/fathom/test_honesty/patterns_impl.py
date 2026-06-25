"""Concrete test honesty pattern implementations. (Stubs — logic TBD.)"""

from __future__ import annotations

import ast

from fathom.test_honesty.patterns import PatternHit, TestHonestyPattern


class InternalModuleMockPattern(TestHonestyPattern):
    """Mocking your own internal modules (not external APIs/DBs)."""

    pattern_id = "internal_module_mock"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        # TODO: detect @patch / mocker.patch on internal module paths
        return []


class TautologicalAssertionPattern(TestHonestyPattern):
    """Assertions against mock return values — expect(mockFn()).toBe(mockFn())."""

    pattern_id = "tautological_assertion"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        # TODO: detect assert mock.return_value == mock.return_value style
        return []


class NoFailurePathPattern(TestHonestyPattern):
    """Tests with no possible failure path."""

    pattern_id = "no_failure_path"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        # TODO: detect assertions that always resolve true
        return []


class MockedCoveragePattern(TestHonestyPattern):
    """100% coverage via mocked paths — line runs but behavior untested."""

    pattern_id = "mocked_coverage"

    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        # TODO: correlate with coverage data when available
        return []
