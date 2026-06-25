# Fathom Analyzer

Python CLI and analysis engine for the Fathom risk matrix.

## Commands

```bash
fathom check [PATH]    # One-shot test honesty analysis
fathom watch [PATH]    # Watch mode (not yet implemented)
```

## Modules

- `test_honesty/` — AST analyzers for dishonest test patterns (Python v1)
- `comprehension/` — Behavioral + git-origin scoring model (Phase 3+)
- `claude_client.py` — On-demand explanations via Claude API (Phase 5+)
