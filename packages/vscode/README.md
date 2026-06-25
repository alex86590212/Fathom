# Fathom VS Code Extension

## Run it (Mac / Cursor) — 3 steps

### Step 1 — One-time setup (Terminal)

```bash
pip install -e /Users/baris/projects/Fathom/packages/analyzer
cd /Users/baris/projects/Fathom/packages/vscode
npm install
```

### Step 2 — Open the extension folder

In Cursor: **File → Open Folder** → select:

```
/Users/baris/projects/Fathom/packages/vscode
```

You must open **this folder** (the one with `package.json`), not the whole Fathom repo.

### Step 3 — Press F5

1. Press **F5** (or **Run → Start Debugging**)
2. Choose **"Run Fathom Extension"** if asked
3. A **new Cursor window** opens with `demo-repo` already loaded

In that new window:

- **Cmd+Shift+P** → `Fathom: Check Test Honesty`
- **Cmd+Shift+P** → `Fathom: Show Risk Matrix`
- Open a file under `tests/` to see gutter colors

## Two windows — which is which?

```
┌─────────────────────────────┐     F5      ┌─────────────────────────────┐
│  Window 1 (you code here)   │  ────────►  │  Window 2 (you test here)   │
│  packages/vscode/           │             │  examples/demo-repo/        │
│  Edit extension.ts, etc.    │             │  Run Fathom commands        │
└─────────────────────────────┘             └─────────────────────────────┘
```

After changing extension code: go back to **Window 1**, press **Cmd+Shift+F5** to reload.

## If Fathom can't find the CLI

**Cmd+,** → search `fathom.analyzerPath` → set to:

```
/Users/baris/projects/work_env/bin/fathom
```

(Run `which fathom` in Terminal to confirm your path.)

## Commands

| Command | What it does |
|---------|----------------|
| Fathom: Check Test Honesty | Runs `fathom check` on `tests/` |
| Fathom: Show Risk Matrix | Opens 2×2 panel |

## Hover tooltips

- **Hover any line** in a scanned test file → file zone, honesty & comprehension scores
- **Hover a flagged line** (highlighted) → pattern name + message + scores
- **Status bar** (bottom right) → quick zone summary
