# DDOG Earnings Tracker

Public-data pre-earnings tracker for Datadog (NASDAQ: DDOG). npm nowcast, SEC XBRL cloud control, Wikimedia attention check, lag-1 ridge versus persistence.

**Documentation:** [`docs/README.md`](docs/README.md)  
**Scored write-up:** [`docs/report.md`](docs/report.md)  
**10-slide talk:** [`docs/slides.html`](docs/slides.html) (also `/slides.html` on the dashboard)

## Run everything from `scripts/`

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/analyze.sh
./scripts/test.sh
./scripts/dashboard.sh
```

Open http://127.0.0.1:5173 for the dashboard and http://127.0.0.1:5173/slides.html for the deck. Details: [`docs/runbook.md`](docs/runbook.md).

Zip a packet (no `.venv` / `node_modules` / `.git`):

```bash
./scripts/package_submission.sh
```

That writes `ddog_takehome_submission.zip` at the repo root.

## Live demo

https://ddog-earnings-tracker.vercel.app/

Optional Python UI: `./scripts/streamlit.sh`. Demo Vite in the interview.

## What the numbers say

Fourteen quarters, 2023Q1–2026Q2. `@datadog/browser-rum` YoY correlates 0.86 with revenue YoY in the same quarter (coincident nowcast) and 0.69 at lag 1. AWS segment YoY correlates 0.78 coincident and 0.78 at lag 1. npm lag-1 ridge RMSE 3.3pp; +AWS or +stub ~2.6pp; persistence **2.1pp**. Wikipedia is not coincident (−0.09).

As of 2026-09-01 (63/92 days into 2026Q3): lag-1 call **30.6%** YoY vs last print **35.6%** (behind). Intra-quarter RUM stub **+151%** package YoY — coincident, not a revenue forecast. Company 8-K midpoint ~**28.7%**. Exploratory, not investment advice.

## Legal

Public SEC Company Facts, EDGAR XBRL, npm downloads API, Wikimedia pageviews API. No Google Trends scrape, no job-board scrape. Research aid, not personalized investment advice.
