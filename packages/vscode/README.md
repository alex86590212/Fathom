# Fathom VS Code Extension

Per-developer git-origin comprehension and test honesty heatmap.

## Development

```bash
pip install -e ../analyzer
cd packages/vscode && npm install && npm run compile
# Press F5 to launch Extension Development Host
```

## Commands

- **Fathom: Check Test Honesty** — runs `fathom check tests/ --format json`
- **Fathom: Show Risk Matrix** — 2×2 webview panel with file zones

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `fathom.analyzerPath` | `fathom` | Path to CLI |
| `fathom.dataDir` | `.fathom` | Local scores + last-check |

## Manual test checklist

- [ ] Open demo repo workspace, run Check — status bar shows zone
- [ ] Open `test_dishonest_mocks.py` — gutter tinted critical/fragile
- [ ] Show Matrix — files listed in quadrants, click opens file
- [ ] `.fathom/last-check.json` and `scores.json` written
