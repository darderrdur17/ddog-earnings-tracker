# 15-Minute Presentation Outline (10 slides)

This file is the **talk script**, not a substitute deck. The scored deliverable is `docs/01_take_home_report.md`.

Assignment cap: 10 slides. Timed for 15 minutes + 5 minutes Q&A.  
**Demo the Vite app, not Streamlit.** `cd dashboard && npm run dev` → http://localhost:5173

## Slide 1 — The decision (1:00)

Investors want an early read on usage-sensitive SaaS growth before the print. The question is not “Can a model beat the Street?” It is “Can an analyst see, validate, and explain business activity earlier — with sources and uncertainty showing?”

## Slide 2 — Why Datadog (1:15)

2025 10-K: majority-annual subscriptions; ratable / delivered-as-used / monthly usage plus overage; 90% of ARR from ≥$100k customers; NRR ~120% from existing-customer usage; RPO $3.46bn; grows as customers expand public/private cloud workloads; competes with and sells through AWS/Azure/GCP.

## Slide 3 — Sources: 3 ingested + 1 proposed (1:30)

| # | Source | Status |
|---|---|---|
| 1 | **npm** (`browser-rum` + `dd-trace`) | One source, two packages. Daily public API. **Ingested.** |
| 2 | Hyperscaler cloud (AWS/GCP/MSFT XBRL) | One source. Quarterly SEC. **Macro control**, not HF, not DDOG accounts. |
| 3 | Wikipedia “Datadog” pageviews | ToS-safe attention; empirically weak coincident. Trends not scraped. |
| 4 | Hiring / skills | **Not ingested** — licensed vendor only |

## Slide 4 — Method (1:15)

Target: SEC revenue YoY, Q4 = FY − (Q1–Q3). Sample: 14 quarters, 2023Q1–2026Q2. Calendar lead–lag. Ridge on lag-1 npm (**validated call**). Intra-quarter same-calendar-day npm stub = **coincident nowcast**. Ablations: +AWS, +stub. Baselines: persistence + company 8-K guidance (no Street scrape). No future row in training.

## Slide 5 — Lead–lag is a nowcast (1:30)

RUM 0.86 coincident / 0.69 lag-1 — a **coincident nowcast**, weaker lead. Do not call lag-0 a leading indicator. AWS 0.78 / **0.78** lag-1 — cloud regime, not DDOG accounts. GCP 0.95 coincident is AI-infra co-movement. Wiki DDOG −0.09 coincident; New Relic wiki negative.

## Slide 6 — Walk-forward + stub (1:30)

Eight OOS forecasts. Persistence RMSE **2.1pp**. npm ridge **3.3pp**. npm+AWS **2.6pp**. Lag-1+stub **2.6pp** — still loses to persistence. 2026Q3 lag-1 call **30.6%** vs last print **35.6%** — **behind**. Stub through 3 Sep: RUM **+140%** package YoY (65/92 days) — coincident, not a revenue number. Management 8-K outlook **28.2–29.3%** implied YoY.

## Slide 7 — Live dashboard (3:00)

Open Vite. Walk generated timestamp → KPIs → stub strip (lag-1 vs coincident stub) → charts → call construction → lead–lag → walk-forward vs persistence → sources. Ahead/behind is ±1pp vs last reported YoY, not Street.

## Slide 8 — What exists vs what I would ship (1:15)

**Built:** Python collectors (SEC, XBRL, npm, Wikimedia), ridge walk-forward, intra-quarter stub, tests, annotated React/Vite dashboard.  
**Not built:** Next.js/tRPC production app. That is a roadmap, not this packet.

## Slide 9 — Limits and next test (1:00)

Small *n*; npm CI; Q4 residual; wiki news spikes; no consensus vendor (company 8-K only). Next: licensed hiring, placebo non-Datadog npm, one full earnings cycle.

## Slide 10 — Close (0:30)

Start narrow, public, reproducible. Prove the workflow. Show uncertainty. I would rather be wrong with a cited persistence and 8-K baseline than look precise without one.

## Likely Q&A (5:00)

**Why not ingest hiring?** Job boards’ terms forbid scraping. Gutiérrez et al. (2020) supports the *logic*. Production would license LinkUp/Revelio/Thinknum.

**Why not Google Trends?** No official public API. Wikimedia is the ToS-safe attention series. Empirically it does **not** nowcast DDOG revenue.

**Is Streamlit the product?** No. The presentation surface is the Vite app.

**Does the stub lead earnings?** No. It is coincident (corr 0.87 vs eventual revenue YoY). Adding it to walk-forward still loses to persistence.

**How do you prevent leakage?** Calendar lags, expanding-window training, lag-1 call uses no same-quarter npm. Stub features in the optional variant are known as of the stub date.

**NRR / RPO / $100k customers?** 10-K disclosures, not a usable quarterly Company Facts series.
