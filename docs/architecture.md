# Architecture

## Three Layers

```
┌─────────────────────────────────────────────────────────┐
│  VS Code Extension (packages/vscode)                    │
│  Behavioral tracking · gutter heatmap · Claude hover   │
└────────────────────────┬────────────────────────────────┘
                         │ reads/writes .fathom/
┌────────────────────────▼────────────────────────────────┐
│  Analyzer CLI (packages/analyzer)                       │
│  test_honesty · comprehension · claude_client         │
└────────────────────────┬────────────────────────────────┘
                         │ invoked by
┌────────────────────────▼────────────────────────────────┐
│  GitHub Action (packages/github-action)                 │
│  Comment-only PR risk reports                           │
└─────────────────────────────────────────────────────────┘
```

## Local Data (`.fathom/`)

Per-developer, gitignored:

```
.fathom/
├── signals.json       # behavioral tracking (VS Code extension)
├── scores.json        # comprehension scores per file
└── last-check.json    # most recent CLI analysis results
```

No telemetry. No team sync. No phone-home.

## Privacy

The only external call is to the Claude API, and only when you explicitly hover over a red zone and ask for an explanation.

## Free-tier rules

Core scoring uses local AST + git rules only. See [rules.md](./rules.md) for pattern definitions, thresholds, penalties, and explicit non-goals.
