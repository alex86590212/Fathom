"""Comprehension types and base scores."""

from __future__ import annotations

from enum import Enum


class CodeOrigin(Enum):
    WRITTEN_FROM_SCRATCH = "written_from_scratch"
    HEAVILY_MODIFIED_AI = "heavily_modified_ai"
    LIGHTLY_TOUCHED_AI = "lightly_touched_ai"
    AI_GENERATED_UNOPENED = "ai_generated_unopened"


ORIGIN_BASE_SCORES: dict[CodeOrigin, int] = {
    CodeOrigin.WRITTEN_FROM_SCRATCH: 70,
    CodeOrigin.HEAVILY_MODIFIED_AI: 50,
    CodeOrigin.LIGHTLY_TOUCHED_AI: 20,
    CodeOrigin.AI_GENERATED_UNOPENED: 5,
}
