# 10-slide talk (15 minutes + 5 Q&A)

Speaker script for [slides.html](slides.html) — also served at `/slides.html` on the dashboard. The scored write-up is [report.md](report.md).

**Demo the Vite app, not Streamlit:** `./scripts/dashboard.sh` → http://127.0.0.1:5173

## Slide 1 — What we are deciding (1:00)

Can an analyst see Datadog activity before the print — with sources and uncertainty showing?

2026Q3 lag-1 ridge: **30.6%** YoY. Last print: **35.6%** · $1,121m. 8-K midpoint: **28.7%**. Tracking **behind** last print (±1pp rule). Persistence still wins walk-forward; that honesty is the assignment.

## Slide 2 — Why Datadog (1:15)

2025 10-K: mostly annual subscriptions; ratable / delivered-as-used / monthly usage plus overage; 90% of ARR from ≥$100k customers; NRR ~120% from existing-customer usage; RPO $3.46bn; grows as customers expand cloud workloads; sells through AWS / Azure / GCP. NRR / RPO / large-customer counts are annual disclosures, not a quarterly series we nowcast.

## Slide 3 — Sources: 3 ingested + 1 proposed (1:30)

1. **npm** (`browser-rum` + `dd-trace`) — one source, two packages. Daily public API. Ingested.
2. Hyperscaler cloud XBRL — one source. Quarterly SEC. Macro control, not HF, not DDOG accounts.
3. Wikipedia “Datadog” pageviews — ToS-safe attention; empirically weak coincident. Trends not scraped.
4. Hiring / skills — not ingested; licensed vendor only.

## Slide 4 — Method (1:15)

Target: SEC revenue YoY; Q4 = FY − (Q1–Q3). Sample: 14 quarters, 2023Q1–2026Q2. Calendar lead–lag. Ridge on lag-1 npm = **validated call**. Intra-quarter same-calendar-day npm stub = **coincident nowcast** (through 1 Sep, 63/92 days). Ablations: +AWS, +stub. Baselines: persistence + company 8-K. No Street scrape. No future row in training.

## Slide 5 — Lead–lag is a nowcast (1:30)

RUM 0.86 coincident / 0.69 lag-1 — coincident nowcast, weaker lead. Do not call lag-0 a leading indicator. AWS 0.78 / 0.78 lag-1 — cloud regime, not DDOG accounts. GCP 0.95 coincident is AI-infra co-movement. Wiki DDOG −0.09; New Relic wiki negative.

## Slide 6 — Walk-forward + stub (1:30)

Eight OOS forecasts. Persistence RMSE **2.1pp**. npm ridge **3.3pp**. npm+AWS **2.6pp**. Lag-1+stub **2.6pp** — still loses to persistence. 2026Q3 call **30.6%** vs last print **35.6%** — behind. Stub: RUM **+151%** package YoY (63/92 days) — not a revenue number. 8-K implied YoY **28.2–29.3%**.

## Slide 7 — Live dashboard (3:00)

Open Vite. Timestamp → call stack → KPIs → stub strip → charts → call construction → lead–lag → walk-forward vs persistence → sources. Ahead/behind is ±1pp vs last reported YoY, not Street.

## Slide 8 — What shipped vs what I would ship (1:15)

**Built:** Python collectors (SEC, XBRL, npm, Wikimedia), ridge walk-forward, intra-quarter stub, 22 tests, annotated React/Vite dashboard.

**Not built:** Next.js/tRPC production app. That is a roadmap — see [technical-design.md](technical-design.md) — not this packet.

## Slide 9 — Limits and next test (1:00)

Small *n*; npm CI; Q4 residual; wiki news spikes; no consensus vendor (company 8-K only). Next: licensed hiring, placebo non-Datadog npm, one full earnings cycle.

## Slide 10 — Close (0:30)

Start narrow, public, reproducible. Prove the workflow. Show uncertainty. I would rather be wrong with a cited persistence and 8-K baseline than look precise without one.

## Likely Q&A (5:00)

**Why not ingest hiring?** Job boards’ terms forbid scraping. Gutiérrez et al. (2020) supports the *logic*. Production would license a vendor.

**Why not Google Trends?** No official public API I was willing to use. Wikimedia is the ToS-safe attention series. Empirically it does **not** nowcast DDOG revenue.

**Is Streamlit the product?** No. The presentation surface is the Vite app.

**Does the stub lead earnings?** No. Coincident (corr 0.86 vs eventual revenue YoY). Adding it still loses to persistence.

**How do you prevent leakage?** Calendar lags, expanding-window training, lag-1 call uses no same-quarter npm. Stub features in the optional variant are known as of the stub date.

**NRR / RPO / $100k customers?** 10-K disclosures, not a usable quarterly Company Facts series.
