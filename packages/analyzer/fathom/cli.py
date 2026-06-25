"""Fathom CLI — `fathom check` / `fathom watch`."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from fathom.test_honesty import analyze_directory

console = Console()


@click.group()
@click.version_option(package_name="fathom-analyzer")
def main() -> None:
    """Fathom — code comprehension risk visualization."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
def check(path: Path, output_format: str) -> None:
    """Analyze test honesty for Python tests under PATH."""
    console.print(f"[dim]Analyzing tests in {path}…[/dim]")
    results = analyze_directory(path)

    if output_format == "json":
        import json

        console.print_json(json.dumps(results, indent=2))
    else:
        if not results["findings"]:
            console.print("[green]No dishonest test patterns detected.[/green]")
        else:
            console.print(f"[yellow]{len(results['findings'])} finding(s):[/yellow]")
            for finding in results["findings"]:
                console.print(f"  • {finding['file']}:{finding['line']} — {finding['pattern']}")

    # Exit 0 always for now; GitHub Action handles reporting separately
    sys.exit(0)


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def watch(path: Path) -> None:
    """Watch PATH and re-run analysis on changes. (Not yet implemented.)"""
    console.print("[yellow]fathom watch is not yet implemented.[/yellow]")
    sys.exit(1)


if __name__ == "__main__":
    main()
