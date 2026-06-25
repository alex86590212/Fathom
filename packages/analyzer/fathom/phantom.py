"""Animated pixel-art phantom for CLI deep checks."""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from typing import Generator

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

# Sprite frames: bob (0,1), blink variant uses frame 2 for eyes
_FRAME_BOB_UP = [
    "    ▄▄▄▄▄▄▄    ",
    "  ▄████████▄  ",
    " ████▀  ▀████ ",
    "████  ■■  ████",
    "████  ▄▄  ████",
    " ████▄▄▄▄████ ",
    "  ▀██▄▄▄▄██▀  ",
    "   ▀▄▄▄▄▄▀   ",
]

_FRAME_BOB_DOWN = [
    "              ",
    "    ▄▄▄▄▄▄▄    ",
    "  ▄████████▄  ",
    " ████▀  ▀████ ",
    "████  ■■  ████",
    "████  ▄▄  ████",
    " ████▄▄▄▄████ ",
    "  ▀██▄▄▄▄██▀  ",
]

_FRAME_BLINK = [
    "    ▄▄▄▄▄▄▄    ",
    "  ▄████████▄  ",
    " ████▀  ▀████ ",
    "████  ──  ████",
    "████  ▄▄  ████",
    " ████▄▄▄▄████ ",
    "  ▀██▄▄▄▄██▀  ",
    "   ▀▄▄▄▄▄▀   ",
]

_MIN_DISPLAY_SEC = 0.8


def _styled_sprite(lines: list[str]) -> Text:
    text = Text()
    for i, line in enumerate(lines):
        if i > 0:
            text.append("\n")
        for ch in line:
            if ch == "█":
                text.append(ch, style="bold white")
            elif ch == "▄":
                text.append(ch, style="white")
            elif ch == "▀":
                text.append(ch, style="dim white")
            elif ch == "■":
                text.append(ch, style="bold black on white")
            elif ch == "─":
                text.append(ch, style="dim")
            else:
                text.append(ch, style="dim white")
    return text


def should_show_mascot(
    *,
    output_format: str,
    no_mascot: bool,
    is_tty: bool | None = None,
) -> bool:
    if no_mascot or output_format == "json":
        return False
    if output_format == "markdown":
        return False
    tty = is_tty if is_tty is not None else sys.stdout.isatty()
    if not tty:
        return False
    import os

    if os.environ.get("NO_COLOR"):
        return False
    return True


class PhantomAnimator:
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()
        self._status = "Peering into tests…"
        self._tick = 0
        self._live: Live | None = None
        self._start: float = 0.0

    def set_status(self, msg: str) -> None:
        self._status = msg

    def _render(self) -> Group:
        self._tick += 1
        blink = self._tick % 12 == 0
        bob = (self._tick // 3) % 2 == 0
        if blink:
            sprite = _FRAME_BLINK
        elif bob:
            sprite = _FRAME_BOB_UP
        else:
            sprite = _FRAME_BOB_DOWN
        return Group(
            _styled_sprite(sprite),
            Text(self._status, style="dim italic"),
        )

    def __enter__(self) -> PhantomAnimator:
        self._start = time.monotonic()
        self._live = Live(self._render(), console=self._console, refresh_per_second=8)
        self._live.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        if self._live:
            elapsed = time.monotonic() - self._start
            if elapsed < _MIN_DISPLAY_SEC:
                time.sleep(_MIN_DISPLAY_SEC - elapsed)
            self._live.__exit__(*args)


@contextmanager
def animate(
    enabled: bool = True,
    status: str = "Peering into tests…",
    console: Console | None = None,
) -> Generator[PhantomAnimator, None, None]:
    anim = PhantomAnimator(console=console)
    anim.set_status(status)
    if not enabled:
        yield anim
        return
    with anim:
        yield anim
