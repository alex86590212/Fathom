# Fathom GitHub Action

Posts a **comment-only** risk matrix summary on pull requests. Never blocks merge.

```yaml
# .github/workflows/fathom.yml
name: Fathom
on: [pull_request]
jobs:
  fathom:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: ./packages/github-action
        with:
          path: examples/demo-repo/tests
```

Build locally:

```bash
cd packages/github-action && npm install && npm run build
```

Hard-fail mode (`fail_on: critical`) is deferred.
