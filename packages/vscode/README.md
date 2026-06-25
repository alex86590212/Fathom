# Fathom VS Code Extension

Per-developer behavioral tracking and gutter heatmap. All data stays in `.fathom/` (gitignored).

## Development

```bash
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

## Modules

- `extension.ts` — entry point, command registration
- `tracker.ts` — behavioral signal collection (reading time, AI completions)
- `heatmap.ts` — gutter decorations from risk scores
- `explainer.ts` — Claude API hover explanations (explicit user action only)
