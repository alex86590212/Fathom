"""Smoke tests for CLI skeleton."""

from click.testing import CliRunner

from fathom.cli import main


def test_check_runs_on_empty_dir(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["check", str(tmp_path)])
    assert result.exit_code == 0
    assert "Analyzing" in result.output


def test_watch_not_implemented(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["watch", str(tmp_path)])
    assert result.exit_code == 1
    assert "not yet implemented" in result.output
