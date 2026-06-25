# Fathom

Code comprehension risk visualization. Every file in your codebase lives in a 2×2 risk matrix — Fathom shows you where each file sits and helps move it toward green.

## The 2×2 Risk Matrix

|  | **Low test honesty** | **High test honesty** |
|---|---|---|
| **Low comprehension** | 🔴 Critical risk | 🟡 Fragile confidence |
| **High comprehension** | 🟡 Blind spots | 🟢 Healthy |

## Architecture

Three layers, built in phases:

| Phase | Package | Status |
|-------|---------|--------|
| 1 | `packages/analyzer` — Python CLI (`fathom check`) | Done |
| 2 | `packages/github-action` — PR comment-only | Done |
| 3 | `packages/vscode` — Heatmap + git origin | Done |

## Quick Start

```bash
# Install analyzer (dev)
cd packages/analyzer
pip install -e ".[dev]"

# Run test honesty check (Python tests only, v1)
fathom check tests/
```

## Privacy

Everything stays local by default. The `.fathom/` directory lives in your repo (gitignored). No telemetry, no phone-home, no account required. The only external call is to the Claude API, and only when you explicitly hover over a red zone and ask for an explanation.

## Repo Structure

```
fathom/
├── packages/
│   ├── analyzer/          # Python CLI + analysis engine
│   ├── vscode/            # VS Code extension (TypeScript)
│   └── github-action/     # GitHub Action (comment-only)
├── docs/
├── examples/demo-repo/
└── README.md
```

## Design Decisions

- **Behavioral tracking:** per-developer, local only (no team sync)
- **Test analysis:** Python-only (pytest/unittest) in v1; JS/TS in v1.1
- **GitHub Action:** comment-only on PRs; hard-fail mode deferred
