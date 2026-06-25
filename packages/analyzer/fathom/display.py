"""Rich terminal UI for Fathom CLI output."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

ZONE_META: dict[str, tuple[str, str, str]] = {
    "critical": ("red", "Critical", "Low comprehension · dishonest tests"),
    "fragile": ("yellow", "Fragile", "Low comprehension · tests look honest"),
    "blind_spot": ("blue", "Blind spot", "You understand it · tests lie"),
    "healthy": ("green", "Healthy", "Good comprehension · honest tests"),
}

PATTERN_LABELS: dict[str, str] = {
    "internal_module_mock": "Internal mock",
    "tautological_assertion": "Tautology",
    "no_failure_path": "Can't fail",
    "mocked_coverage": "Mocked coverage",
}


def _score_style(value: float, *, invert: bool = False) -> str:
    """Color score: green = good, red = bad. Honesty uses invert=False."""
    if invert:
        value = 100 - value
    if value < 50:
        return "red"
    if value < 80:
        return "yellow"
    return "green"


def _zone_badge(zone: str) -> Text:
    color, label, _ = ZONE_META.get(zone, ("white", zone, ""))
    return Text(f" {label} ", style=f"bold {color} on {color}22")


def _matrix_panel(summary: dict[str, int]) -> Panel:
    """2×2 risk matrix with live counts."""
    def cell(zone: str, row_label: str, col_label: str) -> str:
        count = summary.get(zone, 0)
        color, label, _ = ZONE_META[zone]
        count_str = f"[bold {color}]{count}[/]" if count else "[dim]0[/]"
        return f"[dim]{row_label}[/] × [dim]{col_label}[/]\n{count_str} [bold]{label}[/]"

    grid = Table.grid(padding=(0, 3))
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_row(
        cell("critical", "Low comprehension", "Low honesty"),
        cell("fragile", "Low comprehension", "High honesty"),
    )
    grid.add_row(
        cell("blind_spot", "High comprehension", "Low honesty"),
        cell("healthy", "High comprehension", "High honesty"),
    )
    return Panel(grid, title="Risk matrix", border_style="dim", box=box.ROUNDED)


def _files_table(files: list[dict[str, Any]]) -> Table:
    table = Table(
        title="Files",
        box=box.SIMPLE_HEAD,
        show_edge=False,
        pad_edge=False,
        expand=True,
    )
    table.add_column("Test file", style="bold", ratio=3)
    table.add_column("Zone", ratio=2)
    table.add_column("Honesty", justify="right", ratio=1)
    table.add_column("Comprehension", justify="right", ratio=1)
    table.add_column("Findings", justify="right", ratio=1)

    for fr in files:
        zone = fr["risk_zone"]
        finding_count = len(fr.get("findings", []))
        findings_display = (
            f"[red]{finding_count}[/]" if finding_count else "[dim]0[/]"
        )
        table.add_row(
            Path(fr["path"]).name,
            _zone_badge(zone),
            Text(f"{fr['test_honesty_score']:.0f}", style=_score_style(fr["test_honesty_score"])),
            Text(
                f"{fr['comprehension_score']:.0f}",
                style=_score_style(fr["comprehension_score"]),
            ),
            findings_display,
        )
    return table


def _findings_panel(findings: list[dict[str, Any]]) -> Panel:
    if not findings:
        return Panel(
            "[green]No dishonest test patterns detected.[/]\n"
            "[dim]Tests appear to exercise real behavior.[/]",
            title="Findings",
            border_style="green",
            box=box.ROUNDED,
        )

    table = Table(box=None, show_header=True, header_style="bold dim", pad_edge=False)
    table.add_column("Location", style="cyan", ratio=2)
    table.add_column("Issue", ratio=1)
    table.add_column("What's wrong", ratio=4)

    for f in findings:
        file_name = Path(f["file"]).name
        pattern = f.get("pattern", "")
        label = PATTERN_LABELS.get(pattern, pattern)
        table.add_row(
            f"{file_name}:{f['line']}",
            f"[yellow]{label}[/]",
            f.get("message", ""),
        )

    return Panel(
        table,
        title=f"[yellow]{len(findings)}[/] finding{'s' if len(findings) != 1 else ''}",
        border_style="yellow",
        box=box.ROUNDED,
    )


def _headline(report_dict: dict[str, Any], path: str) -> Text:
    scanned = report_dict.get("files_scanned", 0)
    findings = len(report_dict.get("findings", []))
    summary = report_dict.get("summary", {})
    critical = summary.get("critical", 0)

    line = Text()
    line.append("Fathom", style="bold")
    line.append(f"  ·  {scanned} test file{'s' if scanned != 1 else ''}")
    if findings:
        line.append(f"  ·  ", style="dim")
        line.append(f"{findings} issue{'s' if findings != 1 else ''}", style="yellow")
    else:
        line.append("  ·  ", style="dim")
        line.append("all clear", style="green")
    if critical:
        line.append("  ·  ", style="dim")
        line.append(f"{critical} critical", style="bold red")
    line.append("\n")
    line.append(path, style="dim")
    return line


def print_report(console: Console, report_dict: dict[str, Any], *, path: str = "") -> None:
    """Render a full human-friendly check report."""
    display_path = path or report_dict.get("path", ".")
    console.print()
    console.print(Panel(_headline(report_dict, display_path), box=box.ROUNDED, border_style="blue"))
    console.print()

    summary = report_dict.get("summary", {})
    files = report_dict.get("files", [])
    scanned = report_dict.get("files_scanned", 0)

    if scanned == 0:
        console.print(
            Panel(
                "[dim]No Python test files found here.[/]\n"
                "Look for [bold]test_*.py[/] or [bold]*_test.py[/] under this path.",
                title="Nothing to scan",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
        console.print()
        return

    if files:
        console.print(_matrix_panel(summary))
        console.print()
        console.print(_files_table(files))
        console.print()

    console.print(_findings_panel(report_dict.get("findings", [])))

    if report_dict.get("findings"):
        console.print()
        console.print(
            "[dim]Tip:[/] Run [bold]fathom watch[/] while fixing tests for live feedback."
        )
    console.print()


def print_watch_header(console: Console, watch_path: str) -> None:
    console.print()
    console.print(
        Panel(
            f"[bold]Fathom watch[/]  ·  [dim]{watch_path}[/]\n"
            "[dim]Saving on each run → .fathom/last-check.json  ·  Ctrl+C to stop[/]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()


def print_watch_diff(
    console: Console,
    *,
    new: set[tuple],
    resolved: set[tuple],
) -> None:
    console.print(Rule(style="dim"))
    ts = Text()
    ts.append(time_stamp(), style="dim")
    ts.append("  scan complete", style="bold")
    console.print(ts)

    if not new and not resolved:
        console.print("[dim]No change since last scan.[/]")
        return

    parts: list[str] = []
    if new:
        parts.append(f"[red]+{len(new)} new[/]")
    if resolved:
        parts.append(f"[green]-{len(resolved)} resolved[/]")
    console.print("  ".join(parts))


def print_score(console: Console, file: Path, score: float, origin: str) -> None:
    origin_labels = {
        "written_from_scratch": "Written from scratch",
        "heavily_modified_ai": "Heavily modified after AI drop",
        "lightly_touched_ai": "Lightly touched after AI drop",
        "ai_generated_unopened": "Bulk drop · barely revisited",
    }
    label = origin_labels.get(origin, origin)
    score_line = Text("Comprehension  ")
    score_line.append(f"{score:.0f}", style=_score_style(score))
    origin_line = Text("Origin  ", style="dim")
    origin_line.append(label)

    console.print()
    console.print(
        Panel(
            Group(Text(file.name, style="bold"), score_line, origin_line),
            title="Fathom score",
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()


def time_stamp() -> str:
    import time

    return time.strftime("%H:%M:%S")
