"""CLI tests."""

import json
from pathlib import Path

from click.testing import CliRunner

from fathom.cli import main

DEMO_TESTS = Path(__file__).resolve().parents[3] / "examples" / "demo-repo" / "tests"


def test_check_json_stdout(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["check", str(tmp_path), "--format", "json", "--no-mascot"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "files_scanned" in data
    assert "summary" in data


def test_check_no_mascot_text(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["check", str(tmp_path), "--no-mascot"])
    assert result.exit_code == 0
    assert "files scanned" in result.output.lower() or "No dishonest" in result.output


def test_check_writes_fathom_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["check", str(DEMO_TESTS), "--no-mascot", "--no-git"],
    )
    assert result.exit_code == 0
    assert (tmp_path / ".fathom" / "last-check.json").is_file()


def test_check_markdown_format():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["check", str(DEMO_TESTS), "--format", "markdown", "--no-mascot", "--no-git"],
    )
    assert result.exit_code == 0
    assert "fathom-report" in result.output


def test_score_command(tmp_path):
    f = tmp_path / "test_x.py"
    f.write_text("def test_a(): assert True\n")
    runner = CliRunner()
    result = runner.invoke(main, ["score", str(f), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "comprehension_score" in data
