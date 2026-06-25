# Demo Repo

A small Python project with intentionally dishonest tests for Fathom demos.

## Purpose

Run `fathom check examples/demo-repo/tests/` to see real findings once pattern detectors are implemented.

## Test files (stubs)

- `tests/test_honest.py` — clean tests (should score green)
- `tests/test_dishonest_mocks.py` — internal module mocking theater
- `tests/test_tautological.py` — assertions against mock return values
