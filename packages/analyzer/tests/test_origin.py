"""Tests for git origin detection."""

from pathlib import Path
from unittest.mock import patch

from fathom.comprehension import CodeOrigin, detect_origin, score_file


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


def test_detect_origin_ai_only_commits():
    commit = "a" * 40
    blame = f"{commit} 1 1 1\nauthor Foo\nprevious xyz\nfilename t.py\n\tcode\n"

    def fake_git(args, cwd):
        if args[:2] == ["rev-parse", "--show-toplevel"]:
            return str(cwd)
        if args[:2] == ["blame", "--line-porcelain"]:
            return blame
        if args[:3] == ["log", "-1", "--format=%B"]:
            return "Co-Authored-By: Cursor <cursor@cursor.com>"
        return None

    with patch("fathom.comprehension.origin._run_git", side_effect=fake_git):
        origin = detect_origin(Path("/repo/test.py"))
    assert origin == CodeOrigin.AI_GENERATED_UNOPENED
