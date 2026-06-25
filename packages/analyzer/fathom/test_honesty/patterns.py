"""Test honesty anti-pattern definitions and base classes."""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class PatternHit:
    line: int
    pattern_id: str
    message: str
    severity: str = "warning"


class TestHonestyPattern(ABC):
    """Base class for AST-based test honesty detectors."""

    pattern_id: ClassVar[str]
    _registry: ClassVar[list[type[TestHonestyPattern]]] = []

    def __init__(self, coverage_data: dict | None = None) -> None:
        self.coverage_data = coverage_data

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "pattern_id"):
            TestHonestyPattern._registry.append(cls)

    @classmethod
    def registry(cls) -> list[type[TestHonestyPattern]]:
        return list(cls._registry)

    @abstractmethod
    def detect(self, tree: ast.Module, source: str) -> list[PatternHit]:
        """Return all hits for this pattern in the given AST."""


# Import concrete patterns so they register via __init_subclass__
from fathom.test_honesty import patterns_impl  # noqa: E402, F401
