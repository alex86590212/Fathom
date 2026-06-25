"""Parse coverage.py JSON reports for mocked-coverage analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_coverage(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def module_has_executed_lines(coverage: dict[str, Any], module_path: str) -> bool:
    """Return True if coverage JSON shows executed lines for a module path fragment."""
    files = coverage.get("files", {})
    for file_key, data in files.items():
        if module_path.replace(".", "/") in file_key.replace("\\", "/"):
            executed = data.get("executed_lines") or data.get("executed_branches")
            if executed:
                return True
    return False
