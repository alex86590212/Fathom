# Demo Repo

A small Python project with intentionally dishonest tests for Fathom demos.

## Purpose

```bash
# Static analysis (no imports needed)
fathom check examples/demo-repo/tests/

# Run tests with pytest
cd examples/demo-repo && pytest -v
# or from repo root:
pytest examples/demo-repo/tests/
```

## Test files

- `tests/test_honest.py` — clean tests (should score green)
- `tests/test_dishonest_mocks.py` — internal module mocking theater
- `tests/test_tautological.py` — assertions against mock return values
- `tests/test_no_failure.py` — assertions that cannot fail
- `tests/test_mocked_coverage.py` — internal patch with coverage correlation

### Coverage demo

```bash
cd examples/demo-repo
coverage run -m pytest
coverage json
fathom check tests/ --coverage coverage.json --no-mascot
```
