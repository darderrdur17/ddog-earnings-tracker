# Run scripts

Executable helpers for setup, analysis, tests, and packaging. Full details: [`docs/runbook.md`](../docs/runbook.md).

Run from repo root:

```bash
chmod +x scripts/*.sh
./scripts/setup.sh && ./scripts/analyze.sh && ./scripts/test.sh && ./scripts/dashboard.sh
```

| Script | Purpose |
|---|---|
| `setup.sh` | venv + pip + npm install |
| `analyze.sh` | fetch data → `outputs/` |
| `dashboard.sh` | Vite dev server |
| `test.sh` | pytest |
| `build.sh` / `preview.sh` | production build + preview |
| `streamlit.sh` | optional Python UI |
| `package_submission.sh` | zip submission packet |
| `export_docs.sh` | regenerate `docs/*.docs` from markdown |
