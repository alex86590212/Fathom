"""Comprehension scoring model — behavioral proxies + git origin. (Phase 3+)"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CodeOrigin(Enum):
    WRITTEN_FROM_SCRATCH = "written_from_scratch"  # base score: 70
    HEAVILY_MODIFIED_AI = "heavily_modified_ai"  # >60% changed, base: 50
    LIGHTLY_TOUCHED_AI = "lightly_touched_ai"  # <10% changed, base: 20
    AI_GENERATED_UNOPENED = "ai_generated_unopened"  # base: 5


ORIGIN_BASE_SCORES: dict[CodeOrigin, int] = {
    CodeOrigin.WRITTEN_FROM_SCRATCH: 70,
    CodeOrigin.HEAVILY_MODIFIED_AI: 50,
    CodeOrigin.LIGHTLY_TOUCHED_AI: 20,
    CodeOrigin.AI_GENERATED_UNOPENED: 5,
}


@dataclass
class ComprehensionScore:
    file_path: Path
    score: float  # 0–100
    origin: CodeOrigin
    signals: dict[str, float]


def score_file(file_path: Path, fathom_dir: Path | None = None) -> ComprehensionScore:
    """Compute comprehension score for a file. (Not yet implemented.)"""
    raise NotImplementedError("Comprehension scoring not yet implemented")


def detect_origin(file_path: Path) -> CodeOrigin:
    """Infer code origin from git blame and commit patterns. (Not yet implemented.)"""
    raise NotImplementedError("Origin detection not yet implemented")
