# Fathom GitHub Action

Posts a **comment-only** risk matrix summary on pull requests. Never blocks merge.

```yaml
# .github/workflows/fathom.yml
name: Fathom
on: [pull_request]
jobs:
  fathom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./packages/github-action  # or fathom/action@v1 when published
        with:
          path: tests/
```

Hard-fail mode (`fail_on: critical`) is deferred.
