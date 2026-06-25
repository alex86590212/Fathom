"""Git-based code origin detection."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from fathom.comprehension.types import CodeOrigin

_AI_PATTERNS = re.compile(
    r"(cursor|copilot|claude|co-authored-by.*(cursor|copilot|claude))",
    re.IGNORECASE,
)


def _run_git(args: list[str], cwd: Path) -> str | None:
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


def _is_ai_commit(message: str) -> bool:
    return bool(_AI_PATTERNS.search(message))


def detect_origin(file_path: Path) -> CodeOrigin:
    """Infer code origin from git blame and commit messages."""
    root = _git_root(file_path.resolve())
    if root is None:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    rel = file_path.resolve()
    try:
        rel = rel.relative_to(root)
    except ValueError:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    blame = _run_git(["blame", "--line-porcelain", str(rel)], root)
    if not blame:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    commits: list[str] = []
    messages: dict[str, str] = {}
    for line in blame.splitlines():
        if line.startswith("author "):
            continue
        if line.startswith("\t"):
            continue
        if re.match(r"^[0-9a-f]{40}", line):
            commit = line.split()[0]
            commits.append(commit)
        if line.startswith("summary "):
            continue
        if line.startswith("previous "):
            continue
        if line.startswith("filename "):
            continue

    # Fetch commit messages for unique commits (cap for performance)
    unique_commits = list(dict.fromkeys(commits))[:40]
    ai_commits = 0
    human_commits = 0
    for commit in unique_commits:
        msg = _run_git(["log", "-1", "--format=%B", commit], root) or ""
        messages[commit] = msg
        if _is_ai_commit(msg):
            ai_commits += 1
        else:
            human_commits += 1

    if not commits:
        return CodeOrigin.WRITTEN_FROM_SCRATCH

    ai_lines = sum(1 for c in commits if _is_ai_commit(messages.get(c, "")))
    ai_ratio = ai_lines / len(commits)

    if ai_ratio == 0:
        return CodeOrigin.WRITTEN_FROM_SCRATCH
    if human_commits == 0:
        return CodeOrigin.AI_GENERATED_UNOPENED
    if ai_ratio < 0.1:
        return CodeOrigin.LIGHTLY_TOUCHED_AI
    if ai_ratio > 0.6:
        return CodeOrigin.HEAVILY_MODIFIED_AI
    return CodeOrigin.LIGHTLY_TOUCHED_AI
