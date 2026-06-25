# Free-tier rules (v1)

Fathom’s free layer is **100% local**: Python `ast` parsing, optional `coverage.json`, and `git blame` structure. No API calls. Rules are designed to be **fast** (one parse + one tree walk per file), **deterministic**, and **conservative** — we flag clear anti-patterns; ambiguous cases are left for optional Claude review (`--ai`, Phase 4+).

## Design principles

| Principle | Meaning |
|-----------|---------|
| **High precision** | Prefer missing a dubious test over flagging a legitimate one |
| **One pass** | Single `ast.parse` + single `ast.walk` per file |
| **Explainable** | Every finding has a stable `pattern` id, line number, and human message |
| **Matrix-safe** | Any finding caps honesty below 50 so zones stay meaningful |
| **AI-ready** | Rule findings are passed to Claude as hints, not replaced by them |

---

## Test honesty (X-axis)

**Question:** Does this test prove real behavior, or only mocks / assertions that cannot fail?

**Score:** Start at **100**. Subtract per-finding penalties (see below). **Any finding caps the score at 49** — one hit always means “low honesty” on the matrix.

**Threshold:** `< 50` or any finding → low honesty.

### Pattern: `internal_module_mock` (−55)

**Triggers when** a test patches **project code** the file already imports (same top-level package), via:

- `@patch("myapp.service.fn")` decorator
- `with patch("myapp.service.fn"):`
- `mocker.patch("myapp.service.fn")` (pytest-mock)
- `patch.multiple("myapp.module", ...)`
- `patch.object(myapp.module, "attr")` when `myapp` is a local import

**Does not trigger when** patching known **external** roots (`requests`, `boto3`, `sqlalchemy`, `openai`, …) or targets whose root module is **not** imported in the test file.

**Rationale:** Mocking your own logic often means the test verifies the mock setup, not production behavior. External I/O mocks are normal.

```python
# FLAGGED — patches imported project code
from demo_app import add
@patch("demo_app.add")
def test_add(mock_add): ...

# OK — patches external HTTP
@patch("requests.get")
def test_fetch(mock_get): ...
```

### Pattern: `tautological_assertion` (−50)

**Triggers when** an `assert` cannot meaningfully fail:

- `assert mock_fn() == mock_fn.return_value` (mock compared to its own return value)
- `assert x == x` where both sides are the same AST subtree (not two independent literals)

**Does not trigger:** `assert 1 == 1` (handled as `no_failure_path` instead).

### Pattern: `no_failure_path` (−35)

**Triggers when** an `assert` is trivially true:

- `assert True`
- `assert 42 == 42` (literal self-equality)

**Rationale:** The test runs but never checks behavior.

### Pattern: `mocked_coverage` (−60, requires `--coverage`)

**Triggers when** both are true:

1. An `internal_module_mock` target would fire for this line, **and**
2. `coverage.json` shows executed lines in that module

**Rationale:** Coverage looks green while internal code is mocked — classic false confidence.

Only runs when `coverage.json` is passed or found next to the scan path.

### Penalties summary

| Pattern | Penalty | Cap alone below 50? |
|---------|---------|---------------------|
| `internal_module_mock` | −55 | Yes |
| `tautological_assertion` | −50 | Yes (with cap) |
| `no_failure_path` | −35 | Yes (with cap) |
| `mocked_coverage` | −60 | Yes |
| Unknown pattern | −25 | Yes (with cap) |

Multiple findings stack (floor 0). Cap at **49** whenever `len(findings) > 0`.

### Explicit non-goals (free tier)

These are **not** rule-detected (too noisy or need AI):

- “Test is too short” / missing assertions
- `assert mock.called` without value checks
- Integration vs unit judgment
- Whether a mock is “necessary”

---

## Comprehension (Y-axis)

**Question:** How likely did the author understand this file, from git history **shape** only?

**No commit messages.** No LLM. Signals: blame concentration, file introduction pattern, post-intro churn.

**Score:** Fixed base per origin (no fractional tuning in v1):

| Origin | Score | Detection |
|--------|-------|-----------|
| `written_from_scratch` | **70** | Lines spread across ≥4 commits; dominant commit holds <40% of lines |
| `heavily_modified_ai` | **50** | Bulk intro visible (≥40% one commit) **and** ≥35% lines from other commits |
| `lightly_touched_ai` | **20** | Whole-file drop (≥80% one commit or added in single commit) with only cosmetic edits |
| `ai_generated_unopened` | **5** | ≥80% lines from one commit **and** follow-up edits on <10% of lines |

**Fallbacks:**

- Not in a git repo → `written_from_scratch` (70)
- `--no-git` on CLI → comprehension **70** for all files (honesty still analyzed)
- Blame unavailable → `written_from_scratch` (70)

**Threshold:** `< 50` → low comprehension.

Phase 4 will add local behavioral signals (reading time, etc.) on top of these bases — still no API.

---

## Risk matrix

Classify each file with thresholds at **50** on both axes:

```
                    Low honesty          High honesty
Low comprehension   CRITICAL             FRAGILE
High comprehension  BLIND_SPOT           HEALTHY
```

---

## Performance budget

| Step | Cost |
|------|------|
| Discover `test_*.py` / `*_test.py` | `rglob` once per directory |
| Per file | 1× `read_text`, 1× `ast.parse`, 1× `ast.walk` |
| Git origin (per file) | 2–3 `git` subprocess calls when enabled |
| Coverage | 1× JSON load per run (shared) |

Target: **< 50ms per typical test file** excluding git. Git dominates on large repos — use `--no-git` for fast honesty-only passes.

---

## Extending rules

New patterns must:

1. Register via `TestHonestyPattern` subclass in `patterns_impl.py`
2. Add penalty in `scoring.py` `PATTERN_PENALTIES`
3. Add label in `display.py` `PATTERN_LABELS`
4. Add tests in `tests/test_patterns.py` with positive **and** negative cases
5. Document here with trigger / non-trigger examples

AI (`claude_client.py`) may **refine** scores later but must not be required for core matrix placement.
