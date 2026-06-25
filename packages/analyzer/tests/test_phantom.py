"""Tests for CLI phantom mascot."""

from fathom.phantom import (
    PhantomAnimator,
    _FRAME_BLINK,
    _FRAME_BOB_DOWN,
    _FRAME_BOB_UP,
    should_show_mascot,
)


def test_sprite_frame_dimensions():
    for frame in (_FRAME_BOB_UP, _FRAME_BOB_DOWN, _FRAME_BLINK):
        assert len(frame) == 8
        assert all(len(line) <= 16 for line in frame)


def test_should_show_mascot_on_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert should_show_mascot(output_format="text", no_mascot=False, is_tty=True)


def test_should_show_mascot_disabled_for_json():
    assert not should_show_mascot(output_format="json", no_mascot=False, is_tty=True)


def test_should_show_mascot_disabled_explicit():
    assert not should_show_mascot(output_format="text", no_mascot=True, is_tty=True)


def test_animator_disabled_context():
    from fathom.phantom import animate

    with animate(enabled=False) as anim:
        anim.set_status("test")
