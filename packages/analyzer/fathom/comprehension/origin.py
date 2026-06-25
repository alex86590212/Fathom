"""Git-based code origin detection from history structure — not commit messages.

People write their own commit messages, so we infer bulk AI/agent patterns from:
- blame concentration (one commit owns most lines)
- low churn after initial bulk introduction
- whole-file addition in a single commit
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from fathom.comprehension.types import CodeOrigin

# Bulk introduction: one commit holds this share of current lines.
_BULK_DOMINANT_RATIO = 0.80
# Still "bulk-shaped" but with meaningful human follow-up edits.
_BULK_REMAINS_RATIO = 0.40
# Human rewrite share on top of a bulk intro.
_HEAVY_REWRITE_RATIO = 0.35
# Tiny follow-up edits after bulk drop (below this → unopened).
_LIGHT_TOUCH_NON_DOMINANT_RATIO = 0.10


def _run_git(args: list[str], cwd: Path) -> str | None:
    import subprocess

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _git_root(file_path: Path) -> Path | None:
    out = _run_git(["rev-parse", "--show-toplevel"], file_path.parent)
    if not out:
        return None
    return Path(out)


def _relative_path(file_path: Path, root: Path) -> Path | None:
    try:
        return file_path.resolve().relative_to(root)
    except ValueError:
        return None


def _parse_blame_commits(blame: str) -> list[str]:
    """Return one commit hash per blamed source line."""
    commits: list[str] = []
    for line in blame.splitlines():
        if line.startswith("\t"):
            continue
        if re.match(r"^[0-9a-f]{40}", line):
            commits.append(line.split()[0])
    return commits


def _blame_stats(commits: list[str]) -> tuple[str, float, int, int, int]:
    """Dominant commit, its line ratio, unique commits, non-dominant line count, total."""
    if not commits:
        return "", 0.0, 0, 0, 0
    counts = Counter(commits)
    dominant, dom_count = counts.most_common(1)[0]
    total = len(commits)
    non_dom_count = total - dom_count
    dom_ratio = dom_count / total
    non_dom_ratio = non_dom_count / total
    return dominant, dom_ratio, len(counts), non_dom_count, total


def _added_in_single_commit(root: Path, rel: Path, dominant: str) -> bool:
    """True when the file first appeared entirely in the dominant commit."""
    log = _run_git(
        ["log", "--diff-filter=A", "--format=%H", "--", str(rel)],
        root,
    )
    if not log:
        return False
    first_add = log.splitlines()[0].strip()
    return first_add.startswith(dominant[: len(first_add)]) or dominant.startswith(first_add)


def detect_origin(file_path: Path) -> CodeOrigin:
    """Infer code origin from blame shape and churn — never from commit messages."""
    root = _git_root(file_path.resolve())
    if root is None:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    rel = _relative_path(file_path, root)
    if rel is None:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    blame = _run_git(["blame", "--line-porcelain", str(rel)], root)
    if not blame:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    commits = _parse_blame_commits(blame)
    if not commits:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    dominant, dom_ratio, unique_commits, non_dom_count, total = _blame_stats(commits)
    single_drop = _added_in_single_commit(root, rel, dominant)
    non_dom_ratio = non_dom_count / total

    # Incremental human authorship: lines spread across many commits.
    if dom_ratio < _BULK_REMAINS_RATIO and unique_commits >= 4:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    # Agentic whole-file drop with no meaningful follow-up edits (<10% lines changed).
    if dom_ratio >= _BULK_DOMINANT_RATIO and non_dom_count * 10 < total:
        return CodeOrigin.AI_GENERATED_UNOPENED

    # Bulk intro still visible but human rewrote a large share.
    if dom_ratio >= _BULK_REMAINS_RATIO and non_dom_ratio >= _HEAVY_REWRITE_RATIO:
        return CodeOrigin.HEAVILY_MODIFIED_AI

    # Bulk-shaped file with cosmetic follow-up edits only.
    if dom_ratio >= _BULK_DOMINANT_RATIO or single_drop:
        return CodeOrigin.LIGHTLY_TOUCHED_AI

    return CodeOrigin.WRITTEN_FROM_SCRATCH
