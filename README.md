# DDOG Earnings Tracker

A public-data, auditable prototype for Datadog (NASDAQ: DDOG) alternative-data research. It converts developer-adoption proxies into a transparent pre-earnings tracker with citations, freshness, and limitations.

The scored write-up is [`docs/01_take_home_report.md`](docs/01_take_home_report.md). [`docs/03_presentation_outline.md`](docs/03_presentation_outline.md) is the **talk script**, not a substitute deck.

## Quick start (presentation)

Demo this — annotated React/Vite dashboard (not Next.js):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/analyze_ddog.py
npm --prefix dashboard install
npm --prefix dashboard run dev
```

Open http://localhost:5173. Tests: `pytest tests -q`. Optional Python UI: `streamlit run src/dashboard.py`.

Production-style static build from repo root:

```bash
python3 src/analyze_ddog.py
npm --prefix dashboard run build
```

The pipeline copies `outputs/analysis_summary.json` into `dashboard/src/` (baked JSON for a prototype). Refresh: re-run the Python command, then rebuild.

Generated files include:

- `data/ddog_sec_revenue.csv`: SEC Company Facts revenue, with Q4 derived as FY residual when needed.
- `data/cloud_*_revenue.csv`: AWS / Google Cloud / MSFT Intelligent Cloud quarterly segment revenue from SEC XBRL.
- `data/wiki_*_monthly.csv`: Wikimedia monthly pageviews (Datadog and New Relic placebo).
- `data/npm_*_daily.csv`: raw daily npm package downloads (chunked ranges).
- `outputs/model_panel.csv`: joined quarterly feature panel.
- `outputs/lead_lag.csv`: zero-to-four quarter lead–lag correlations (YoY vs YoY).
- `outputs/walk_forward_predictions.csv`: expanding-window predictions vs persistence.
- `outputs/analysis_summary.json`: metrics, lag-1 call, intra-quarter stub, and caveats.

## Share the dashboard (public URL)

Reviewers need a link they can open. This is a **static Vite app** with project root `dashboard/` (not a Next.js app).

**Live demo:** https://ddog-earnings-tracker.vercel.app/

Share options:

1. **Vercel** — from a logged-in machine (`npx vercel whoami`). Non-interactive deploys need `--scope`:

   ```bash
   cd dashboard
   npx vercel --yes --scope darderrdur17s-projects
   npx vercel --yes --prod --scope darderrdur17s-projects
   ```

2. **Zip `dashboard/dist`** after `npm --prefix dashboard run build` and host anywhere (S3, Netlify drop, internal static server).

3. **GitHub Pages** from `dashboard/dist` (set Pages to that folder or a `gh-pages` branch of the built files).

If `npx vercel whoami` fails, there is no deploy URL until you log in (`npx vercel login`). Do not use a private Cursor/origin share for this packet.

## Evidence and interpretation

The modeled sample is 14 complete quarters from 2023Q1 through 2026Q2. `@datadog/browser-rum` YoY correlates 0.860 with revenue YoY in the **same** quarter (**coincident nowcast**) and 0.694 at lag 1. AWS segment YoY (SEC XBRL) correlates 0.778 coincident and 0.783 at lag 1. A two-signal npm lag-1 ridge has eight-quarter RMSE 0.033; adding lag-1 AWS or a coincident npm stub cuts that to ~0.026; naive persistence is still better (0.021). Wikipedia “Datadog” pageviews are not coincident (−0.087). Google Trends was not scraped. Hiring is not ingested.

As of 2026-09-03 (65/92 days into 2026Q3): lag-1 ridge call **30.6%** revenue YoY vs last print **35.6%**. Intra-quarter RUM stub **+140%** package YoY (coincident, not a revenue forecast). Company 8-K Q3 outlook implies **~28.7%** YoY at the midpoint. Exploratory, not investment alpha.

## Documentation

- [Take-home research report](docs/01_take_home_report.md) — **scored deliverable**
- [Technical design, API contract, QA/QC, and roadmap](docs/02_technical_design.md)
- [15-minute / 10-slide presentation outline](docs/03_presentation_outline.md) — talk script only

## Legal and research-use boundary

The prototype uses public SEC Company Facts, SEC EDGAR XBRL, the npm downloads API, and the Wikimedia pageviews API. It does not scrape Google Trends, Indeed, or G2. Production connectors must be reviewed for licensing, terms of service, privacy, and point-in-time reproducibility before activation. The product is a research aid, not personalized investment advice.
