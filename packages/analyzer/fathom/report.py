"""Unified Fathom report — per-file zones, scores, findings."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from fathom.comprehension import score_file
from fathom.risk_matrix import RiskZone, classify
from fathom.test_honesty.discovery import discover_test_files
from fathom.test_honesty.analyzers import analyze_file
from fathom.test_honesty.coverage_data import load_coverage
from fathom.test_honesty.scoring import honesty_score

ProgressCallback = Callable[[str], None]

DEFAULT_COMPREHENSION_PLACEHOLDER = 70.0


@dataclass
class FileReport:
    path: str
    test_honesty_score: float
    comprehension_score: float
    risk_zone: str
    origin: str = "written_from_scratch"
    findings: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class FathomReport:
    path: str
    files_scanned: int
    files: list[FileReport]
    summary: dict[str, int]
    findings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _empty_summary() -> dict[str, int]:
    return {zone.value: 0 for zone in RiskZone}


def build_report(
    path: Path,
    coverage_path: Path | None = None,
    use_git_origin: bool = True,
    on_progress: ProgressCallback | None = None,
) -> FathomReport:
    def progress(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    progress("Peering into tests…")
    test_files = discover_test_files(path)
    coverage = load_coverage(coverage_path) if coverage_path else None

    file_reports: list[FileReport] = []
    all_findings: list[dict[str, Any]] = []

    for test_file in test_files:
        findings = analyze_file(test_file, coverage_data=coverage)
        all_findings.extend(findings)
        h_score = honesty_score(findings)

        progress("Tracing git memories…")
        if use_git_origin:
            comp = score_file(test_file)
            c_score = comp.score
            origin = comp.origin.value
        else:
            c_score = DEFAULT_COMPREHENSION_PLACEHOLDER
            origin = "written_from_scratch"

        progress("Weighing honesty…")
        zone = classify(c_score, h_score)

        file_reports.append(
            FileReport(
                path=str(test_file),
                test_honesty_score=h_score,
                comprehension_score=c_score,
                risk_zone=zone.value,
                origin=origin,
                findings=findings,
            )
        )

    if coverage:
        progress("Crossing coverage shadows…")

    summary = _empty_summary()
    for fr in file_reports:
        summary[fr.risk_zone] = summary.get(fr.risk_zone, 0) + 1

    return FathomReport(
        path=str(path),
        files_scanned=len(test_files),
        files=file_reports,
        summary=summary,
        findings=all_findings,
    )


def save_report(report: FathomReport, fathom_dir: Path | None = None) -> Path:
    base = fathom_dir or Path(".fathom")
    base.mkdir(parents=True, exist_ok=True)
    out = base / "last-check.json"
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return out


def format_markdown(report: FathomReport) -> str:
    lines = [
        "## Fathom Risk Report",
        "<!-- fathom-report -->",
        "",
        f"**{report.files_scanned}** test file(s) scanned · "
        f"**{len(report.findings)}** finding(s)",
        "",
        "### Risk matrix",
        "",
        "| Zone | Count |",
        "|------|-------|",
    ]
    for zone in RiskZone:
        count = report.summary.get(zone.value, 0)
        if count:
            lines.append(f"| {zone.value} | {count} |")

    lines.extend(
        [
            "",
            "| | Low test honesty | High test honesty |",
            "|---|---|---|",
            "| **Low comprehension** | critical | fragile |",
            "| **High comprehension** | blind_spot | healthy |",
            "",
        ]
    )

    if report.files:
        lines.append("### Files")
        lines.append("")
        lines.append("| File | Zone | Honesty | Comprehension |")
        lines.append("|------|------|---------|---------------|")
        for fr in report.files:
            name = Path(fr.path).name
            lines.append(
                f"| `{name}` | {fr.risk_zone} | {fr.test_honesty_score:.0f} | "
                f"{fr.comprehension_score:.0f} |"
            )
        lines.append("")

    if report.findings:
        lines.append("### Findings")
        lines.append("")
        for f in report.findings:
            file_name = Path(f["file"]).name
            msg = f.get("message", f["pattern"])
            lines.append(f"- `{file_name}:{f['line']}` — **{f['pattern']}**: {msg}")
        lines.append("")

    lines.append("_Comment-only mode — does not block merge._")
    return "\n".join(lines)
