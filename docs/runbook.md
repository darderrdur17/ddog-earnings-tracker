# Runbook

All scripts run from the repo root. They `cd` to the project root themselves.

## First-time setup

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

Creates `.venv`, installs Python deps, and runs `npm install` in `dashboard/`.

## Typical workflow

```bash
./scripts/analyze.sh    # fetch public data → outputs/ + dashboard JSON
./scripts/test.sh       # pytest (22 tests)
./scripts/dashboard.sh  # Vite dev server → http://127.0.0.1:5173
```

Interview demo: open `/slides.html` on the same origin for the 10-slide deck.

## Scripts

| Script | Purpose |
|---|---|
| `setup.sh` | Create venv, pip install, npm install |
| `analyze.sh` | Fetch SEC / npm / Wikimedia → `outputs/` |
| `dashboard.sh` | Vite dev server (port 5173) |
| `test.sh` | `pytest tests -q` |
| `build.sh` | Static build → `dashboard/dist` |
| `preview.sh` | Serve build (port 4173) |
| `streamlit.sh` | Optional Python UI |
| `package_submission.sh` | Zip reviewable packet at repo root |
| `sync_dashboard_summary.py` | Copy `outputs/analysis_summary.json` into dashboard |
| `export_docs.sh` | Regenerate `docs/*.docs` Word copies from markdown (needs pandoc) |

## Submission zip

```bash
./scripts/package_submission.sh
```

Writes `ddog_takehome_submission.zip` — excludes `.venv`, `node_modules`, `.git`, caches, and build artifacts.

## Live demo

https://ddog-earnings-tracker.vercel.app/

Redeploy after `./scripts/build.sh`: push `dashboard/dist` or connect the repo to Vercel with build command `./scripts/build.sh`.
