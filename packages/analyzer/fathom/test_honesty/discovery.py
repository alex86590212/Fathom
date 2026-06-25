"""Discover Python test files under a path."""

from __future__ import annotations

from pathlib import Path


def discover_test_files(path: Path) -> list[Path]:
    """Find test_*.py and *_test.py files under path."""
    if path.is_file() and path.suffix == ".py":
        return [path]

    patterns = ("test_*.py", "*_test.py")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path.rglob(pattern))
    return sorted(set(files))
