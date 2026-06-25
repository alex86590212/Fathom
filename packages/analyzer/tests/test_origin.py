"""Tests for git origin detection (structural blame, not commit messages)."""

from pathlib import Path
from unittest.mock import patch

from fathom.comprehension import CodeOrigin, detect_origin, score_file

COMMIT_A = "a" * 40
COMMIT_B = "b" * 40
COMMIT_C = "c" * 40


def _blame_block(commit: str, code: str = "x = 1") -> str:
    return f"{commit} 1 1 1\nauthor Foo\nfilename t.py\n\t{code}\n"


def _multi_line_blame(assignments: list[str]) -> str:
    lines: list[str] = []
    for i, commit in enumerate(assignments, start=1):
        lines.append(f"{commit} {i} {i} {i}")
        lines.append("author Foo")
        lines.append("filename t.py")
        lines.append(f"\tline {i}")
    return "\n".join(lines)


def test_detect_origin_no_git(tmp_path):
    f = tmp_path / "test_foo.py"
    f.write_text("x = 1\n")
    assert detect_origin(f) == CodeOrigin.WRITTEN_FROM_SCRATCH


def test_score_file_returns_base_score(tmp_path):
    f = tmp_path / "test_bar.py"
    f.write_text("def test_x(): pass\n")
    score = score_file(f)
    assert score.score == 70.0
    assert score.origin == CodeOrigin.WRITTEN_FROM_SCRATCH


def test_bulk_single_commit_unopened():
    blame = _multi_line_blame([COMMIT_A] * 10)

    def fake_git(args, cwd):
        if args[:2] == ["rev-parse", "--show-toplevel"]:
            return str(cwd)
        if args[:2] == ["blame", "--line-porcelain"]:
            return blame
        if args[:2] == ["log", "--diff-filter=A"]:
            return COMMIT_A
        return None

    with patch("fathom.comprehension.origin._run_git", side_effect=fake_git):
        origin = detect_origin(Path("/repo/test.py"))
    assert origin == CodeOrigin.AI_GENERATED_UNOPENED


def test_bulk_with_light_human_touch():
    # 9 lines bulk, 1 line tweaked in second commit
    blame = _multi_line_blame([COMMIT_A] * 9 + [COMMIT_B])

    def fake_git(args, cwd):
        if args[:2] == ["rev-parse", "--show-toplevel"]:
            return str(cwd)
        if args[:2] == ["blame", "--line-porcelain"]:
            return blame
        if args[:2] == ["log", "--diff-filter=A"]:
            return COMMIT_A
        return None

    with patch("fathom.comprehension.origin._run_git", side_effect=fake_git):
        origin = detect_origin(Path("/repo/test.py"))
    assert origin == CodeOrigin.LIGHTLY_TOUCHED_AI


def test_heavily_modified_after_bulk_intro():
    # 5 lines from bulk intro, 5 lines rewritten later
    blame = _multi_line_blame([COMMIT_A] * 5 + [COMMIT_B] * 5)

    def fake_git(args, cwd):
        if args[:2] == ["rev-parse", "--show-toplevel"]:
            return str(cwd)
        if args[:2] == ["blame", "--line-porcelain"]:
            return blame
        if args[:2] == ["log", "--diff-filter=A"]:
            return COMMIT_A
        return None

    with patch("fathom.comprehension.origin._run_git", side_effect=fake_git):
        origin = detect_origin(Path("/repo/test.py"))
    assert origin == CodeOrigin.HEAVILY_MODIFIED_AI


def test_incremental_authorship_written_from_scratch():
    blame = _multi_line_blame([COMMIT_A, COMMIT_B, COMMIT_C, COMMIT_A, COMMIT_B, COMMIT_C])

    def fake_git(args, cwd):
        if args[:2] == ["rev-parse", "--show-toplevel"]:
            return str(cwd)
        if args[:2] == ["blame", "--line-porcelain"]:
            return blame
        return None

    with patch("fathom.comprehension.origin._run_git", side_effect=fake_git):
        origin = detect_origin(Path("/repo/test.py"))
    assert origin == CodeOrigin.WRITTEN_FROM_SCRATCH
