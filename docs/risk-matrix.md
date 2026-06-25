# The 2×2 Risk Matrix

Two axes. One output.

|  | Low test honesty | High test honesty |
|---|---|---|
| **Low comprehension** | 🔴 Critical risk | 🟡 Fragile confidence |
| **High comprehension** | 🟡 Blind spots | 🟢 Healthy |

Every file in your codebase lives in one of those four zones. Fathom's job is to show you where each file sits and move it toward green.

## Axes

### Comprehension (Y-axis)

Inferred from behavioral proxies — we can't read minds:

| Origin | Base score |
|--------|-----------|
| You wrote it from scratch | 70 |
| Heavily modified AI code (>60% changed) | 50 |
| Lightly touched AI code (<10% changed) | 20 |
| AI generated, you never opened it | 5 |

Signals adjust over time: active reading time increases score; accepting AI completions without edits decreases it. Scores decay as code changes.

### Test Honesty (X-axis)

Four anti-patterns detected via AST analysis:

1. **Internal module mocking** — mocking your own code, not external APIs
2. **Tautological assertions** — `expect(mockFn()).toBe(mockFn())`
3. **No failure path** — assertions that always resolve true
4. **Mocked coverage** — line runs but real behavior untested
