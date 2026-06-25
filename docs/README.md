# Fathom Documentation

## Specs & Plans

| Doc | Description |
|-----|-------------|
| [architecture.md](./architecture.md) | Three-layer architecture overview |
| [risk-matrix.md](./risk-matrix.md) | The 2×2 comprehension × test honesty model |
| [rules.md](./rules.md) | Free-tier detection rules (AST + git), thresholds, non-goals |
| [phases.md](./phases.md) | Build sequence and current status |

## Design Decisions

- Behavioral tracking: **per-developer, local only**
- Test analysis: **Python-only** (pytest/unittest) in v1
- GitHub Action: **comment-only** on PRs
