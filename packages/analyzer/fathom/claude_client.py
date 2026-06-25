"""On-demand Claude API explanations for red-zone code. (Phase 5+)"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExplanationRequest:
    file_path: Path
    line: int
    context: str
    risk_zone: str


@dataclass
class Explanation:
    summary: str
    suggestions: list[str]


def explain(request: ExplanationRequest, api_key: str | None = None) -> Explanation:
    """Request an explanation for a red-zone file/line. Requires explicit user action."""
    raise NotImplementedError("Claude explainer not yet implemented")
