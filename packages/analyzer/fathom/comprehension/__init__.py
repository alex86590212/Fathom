"""Comprehension scoring model — behavioral proxies + git origin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fathom.comprehension.origin import detect_origin as _detect_origin
from fathom.comprehension.types import ORIGIN_BASE_SCORES, CodeOrigin


@dataclass
class ComprehensionScore:
    file_path: Path
    score: float
    origin: CodeOrigin
    signals: dict[str, float]


def detect_origin(file_path: Path) -> CodeOrigin:
    return _detect_origin(file_path)


def score_file(file_path: Path, fathom_dir: Path | None = None) -> ComprehensionScore:
    origin = detect_origin(file_path)
    base = float(ORIGIN_BASE_SCORES[origin])
    return ComprehensionScore(
        file_path=file_path,
        score=base,
        origin=origin,
        signals={"git_origin_base": base},
    )


__all__ = [
    "CodeOrigin",
    "ORIGIN_BASE_SCORES",
    "ComprehensionScore",
    "detect_origin",
    "score_file",
]
