"""Fathom CLI — `fathom check` / `fathom watch` / `fathom score`."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from fathom.comprehension import score_file
from fathom.phantom import animate, should_show_mascot
from fathom.report import build_report, format_markdown, save_report
from fathom.test_honesty import analyze_directory

console = Console()
stderr_console = Console(file=sys.stderr)


def _resolve_coverage(path: Path, coverage: Path | None) -> Path | None:
    if coverage:
        return coverage
    for candidate in (Path("coverage.json"), path / "coverage.json"):
        if candidate.is_file():
            return candidate
    return None


def _print_text_report(report_dict: dict) -> None:
    summary = report_dict.get("summary", {})
    parts = [f"{report_dict['files_scanned']} files scanned"]
    for zone in ("critical", "fragile", "blind_spot", "healthy"):
        if summary.get(zone, 0):
            parts.append(f"{summary[zone]} {zone}")
    console.print("[bold]" + " · ".join(parts) + "[/bold]")

    if report_dict.get("files"):
        table = Table(title="Risk by file")
        table.add_column("File")
        table.add_column("Zone")
        table.add_column("Honesty", justify="right")
        table.add_column("Comprehension", justify="right")
        for fr in report_dict["files"]:
            table.add_row(
                Path(fr["path"]).name,
                fr["risk_zone"],
                f"{fr['test_honesty_score']:.0f}",
                f"{fr['comprehension_score']:.0f}",
            )
        console.print(table)

    findings = report_dict.get("findings", [])
    if not findings:
        console.print("[green]No dishonest test patterns detected.[/green]")
    else:
        console.print(f"\n[yellow]{len(findings)} finding(s):[/yellow]")
        for finding in findings:
            file_name = Path(finding["file"]).name
            console.print(
                f"  • {file_name}:{finding['line']} — "
                f"[bold]{finding['pattern']}[/bold]: {finding.get('message', '')}"
            )


@click.group()
@click.version_option(package_name="fathom-analyzer")
def main() -> None:
    """Fathom — code comprehension risk visualization."""


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
    """Analyze test honesty for Python tests under PATH."""
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

    if not no_save and output_format != "json":
        save_report(report)

    report_dict = report.to_dict()

    if output_format == "json":
        sys.stdout.write(json.dumps(report_dict, indent=2) + "\n")
    elif output_format == "markdown":
        sys.stdout.write(format_markdown(report) + "\n")
    else:
        _print_text_report(report_dict)

    sys.exit(0)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
def score(file: Path, output_format: str) -> None:
    """Score a single file's comprehension from git origin."""
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
        console.print(f"{file.name}: {comp.score:.0f} ({comp.origin.value})")
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
        current = {
            (f["file"], f["line"], f["pattern"]) for f in report.findings
        }
        new = current - self._last_findings
        resolved = self._last_findings - current
        self._last_findings = current

        console.print(f"\n[dim]{time.strftime('%H:%M:%S')}[/dim] — check complete")
        if new:
            console.print(f"[red]+{len(new)} new finding(s)[/red]")
        if resolved:
            console.print(f"[green]-{len(resolved)} resolved[/green]")
        _print_text_report(report.to_dict())


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--coverage", "coverage", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--no-mascot", is_flag=True)
@click.option("--no-git", is_flag=True)
def watch(path: Path, coverage: Path | None, no_mascot: bool, no_git: bool) -> None:
    """Watch PATH and re-run analysis on test file changes."""
    coverage_path = _resolve_coverage(path, coverage)
    handler = _TestWatchHandler(path, coverage_path, no_git, no_mascot)
    handler._run_check()

    observer = Observer()
    watch_path = str(path if path.is_dir() else path.parent)
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()
    console.print(f"[dim]Watching {watch_path} (Ctrl+C to stop)…[/dim]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
