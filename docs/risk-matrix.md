# The 2×2 Risk Matrix

Two axes. One output.

|  | Low test honesty | High test honesty |
|---|---|---|
| **Low comprehension** | 🔴 Critical risk | 🟡 Fragile confidence |
| **High comprehension** | 🟡 Blind spots | 🟢 Healthy |

Every file in your codebase lives in one of those four zones. Fathom's job is to show you where each file sits and move it toward green.

## Axes

### Comprehension (Y-axis)

Inferred from behavioral proxies and git history shape — not commit messages (people write those themselves).

| Origin | Base score | How we detect it |
|--------|-----------|------------------|
| You wrote it from scratch | 70 | Lines spread across many commits; no bulk single-commit drop |
| Heavily modified AI code | 50 | Bulk intro commit still visible, but ≥35% of lines rewritten later |
| Lightly touched AI code | 20 | Whole-file drop in one commit, only cosmetic follow-up edits |
| AI generated, you never opened it | 5 | ≥80% of lines from one commit, ≤2 commits total, file added in one shot |

Phase 4 adds local behavioral signals (reading time, AI completion acceptance) on top of these git-derived bases.

### Test Honesty (X-axis)

Start at **100**. Each finding deducts points and caps the score at **49** — any detected pattern means the file is on the low-honesty side of the matrix.

| Pattern | Penalty |
|---------|---------|
| `internal_module_mock` | −55 |
| `mocked_coverage` | −60 |
| `tautological_assertion` | −50 |
| `no_failure_path` | −35 |

Threshold: **50** — scores below 50 (or any finding) = low test honesty.
