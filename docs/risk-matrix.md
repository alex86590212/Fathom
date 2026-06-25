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

Four anti-patterns detected via AST analysis:

1. **Internal module mocking** — mocking your own code, not external APIs
2. **Tautological assertions** — `expect(mockFn()).toBe(mockFn())`
3. **No failure path** — assertions that always resolve true
4. **Mocked coverage** — line runs but real behavior untested
