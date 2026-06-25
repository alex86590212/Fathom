# Build Phases

| Phase | Timeline | Deliverable | Status |
|-------|----------|-------------|--------|
| 1 | Week 1–2 | Python CLI: `fathom check tests/` | Done |
| 2 | Week 2 | GitHub Action (comment-only) | Done |
| 3 | Week 3–4 | VS Code extension + git origin detector | Done |
| 4 | Week 5 | Behavioral tracking + Claude hover | Planned |
| 5 | Week 6 | Test rewrite suggestions via Claude | Planned |
| 6 | Week 7–8 | Polish, demo video, launch | Planned |

## Phase 1 deliverables

- Unified report with per-file zones and honesty scores
- Four AST patterns including `mocked_coverage` with `--coverage`
- `fathom watch`, animated CLI phantom, `.fathom/last-check.json`
- `fathom score` for single-file git-origin comprehension

## Phase 2 deliverables

- `fathom check --format markdown` for PR comments
- Node 20 GitHub Action with comment upsert via `<!-- fathom-report -->`
- `.github/workflows/fathom.yml` on demo repo tests

## Phase 3 deliverables

- Git origin detection via `git blame` structure (bulk drops, churn) — not commit messages
- VS Code heatmap, status bar, risk matrix webview
- `.fathom/scores.json` persistence from extension
