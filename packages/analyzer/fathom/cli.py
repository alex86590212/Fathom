"""Fathom CLI — `fathom check` / `fathom watch` / `fathom score`."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from fathom.comprehension import score_file
from fathom.display import print_report, print_score, print_watch_diff, print_watch_header
from fathom.phantom import animate, should_show_mascot
from fathom.report import build_report, format_markdown, save_report

console = Console()
stderr_console = Console(file=sys.stderr)


def _resolve_coverage(path: Path, coverage: Path | None) -> Path | None:
    if coverage:
        return coverage
    for candidate in (Path("coverage.json"), path / "coverage.json"):
        if candidate.is_file():
            return candidate
    return None


@click.group()
@click.version_option(package_name="fathom-analyzer", prog_name="fathom")
def main() -> None:
    """Fathom — see which tests you trust and which code you understand."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--format", "output_format", type=click.Choice(["text", "json", "markdown"]), default="text")
@click.option("--coverage", "coverage", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--no-save", is_flag=True, help="Do not write .fathom/last-check.json")
@click.option("--no-mascot", is_flag=True, help="Disable animated phantom")
@click.option("--no-git", is_flag=True, help="Skip git origin detection")
def check(
    path: Path,
    output_format: str,
    coverage: Path | None,
    no_save: bool,
    no_mascot: bool,
    no_git: bool,
) -> None:
    """Analyze test honesty under PATH and map files to the risk matrix."""
    coverage_path = _resolve_coverage(path, coverage)
    show_mascot = should_show_mascot(output_format=output_format, no_mascot=no_mascot)

    def run_build(on_progress=None):
        return build_report(
            path,
            coverage_path=coverage_path,
            use_git_origin=not no_git,
            on_progress=on_progress,
        )

    if show_mascot:
        with animate(enabled=True, console=stderr_console) as phantom:
            report = run_build(on_progress=phantom.set_status)
    else:
        report = run_build()

    saved = None
    if not no_save and output_format != "json":
        saved = save_report(report)

    report_dict = report.to_dict()

    if output_format == "json":
        sys.stdout.write(json.dumps(report_dict, indent=2) + "\n")
    elif output_format == "markdown":
        sys.stdout.write(format_markdown(report) + "\n")
    else:
        print_report(console, report_dict, path=str(path.resolve()))
        if saved is not None:
            console.print(f"[dim]Saved → {saved}[/dim]\n")

    sys.exit(0)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
def score(file: Path, output_format: str) -> None:
    """Show git-derived comprehension score for a single file."""
    comp = score_file(file)
    data = {
        "path": str(file),
        "comprehension_score": comp.score,
        "origin": comp.origin.value,
        "signals": comp.signals,
    }
    if output_format == "json":
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
    else:
        print_score(console, file, comp.score, comp.origin.value)
    sys.exit(0)


class _TestWatchHandler(FileSystemEventHandler):
    def __init__(self, path: Path, coverage: Path | None, no_git: bool, no_mascot: bool) -> None:
        self._path = path
        self._coverage = coverage
        self._no_git = no_git
        self._no_mascot = no_mascot
        self._last_run = 0.0
        self._last_findings: set[tuple] = set()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = event.src_path
        if not src.endswith(".py"):
            return
        name = Path(src).name
        if not (name.startswith("test_") or name.endswith("_test.py")):
            return
        now = time.monotonic()
        if now - self._last_run < 0.5:
            return
        self._last_run = now
        self._run_check()

    def _run_check(self) -> None:
        show_mascot = should_show_mascot(output_format="text", no_mascot=self._no_mascot)

        def run_build(on_progress=None):
            return build_report(
                self._path,
                coverage_path=self._coverage,
                use_git_origin=not self._no_git,
                on_progress=on_progress,
            )

        if show_mascot:
            with animate(enabled=True, console=stderr_console) as phantom:
                report = run_build(on_progress=phantom.set_status)
        else:
            report = run_build()

        save_report(report)
        current = {(f["file"], f["line"], f["pattern"]) for f in report.findings}
        new = current - self._last_findings
        resolved = self._last_findings - current
        self._last_findings = current

        print_watch_diff(console, new=new, resolved=resolved)
        print_report(console, report.to_dict(), path=str(self._path.resolve()))


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--coverage", "coverage", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--no-mascot", is_flag=True)
@click.option("--no-git", is_flag=True)
def watch(path: Path, coverage: Path | None, no_mascot: bool, no_git: bool) -> None:
    """Re-run analysis whenever a test file changes."""
    coverage_path = _resolve_coverage(path, coverage)
    handler = _TestWatchHandler(path, coverage_path, no_git, no_mascot)

    watch_path = str(path.resolve() if path.is_dir() else path.parent.resolve())
    print_watch_header(console, watch_path)
    handler._run_check()

    observer = Observer()
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[dim]Watch stopped.[/]")
    observer.join()


if __name__ == "__main__":
    main()
