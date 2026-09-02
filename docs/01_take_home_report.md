# DDOG Alternative Data Research

**Take-home:** Alternative Data Research — Datadog (NASDAQ: DDOG)  
**Date:** 2 September 2026  
**Scope:** Public SEC Company Facts, SEC XBRL cloud segments, npm downloads, Wikimedia pageviews. Hiring is licensed-only and was not scraped. Not investment advice.

The 10-slide file is a **talk script**, not a substitute deck. The scored write-up is this report.

## Executive conclusion

Three sources were **ingested** (npm, hyperscaler XBRL, Wikimedia) plus one **proposed** (hiring). `@datadog/browser-rum` **nowcasts** Datadog revenue growth (0.86 coincident, 0.69 at lag 1). AWS segment YoY is a **cloud-regime control** (0.78 coincident and 0.78 at lag 1), not a Datadog account meter. Adding lag-1 AWS to the npm ridge cuts eight-quarter RMSE from **3.3pp to 2.6pp**; persistence remains best at **2.1pp**. Wikipedia “Datadog” pageviews are not coincident (−0.09).

**Call (validated lag-1 ridge, npm through 2026Q2):** **30.6%** revenue YoY for **2026Q3** vs last print **35.6%** — **tracking behind**. **Intra-quarter stub (through 2026-09-02, 64/92 days):** RUM downloads **+139%** YoY vs the same Jul 1–Sep 2 window in 2025; `dd-trace` **+138%**. That is a **coincident** package-download update, not a revenue forecast and not a lead. Company 8-K outlook for Q3 2026 is **$1.135–1.145bn** (**28.2–29.3%** implied YoY vs 2025Q3). Ridge sits between last print and management guidance.

## 1. Data selection and rationale

**Shared Datadog mechanism (2025 Form 10-K).** Subscriptions are primarily monthly, annual, or multi-year; the majority of revenue is annual. Customers buy committed usage recognized ratably, committed usage delivered as used, or monthly usage, with incremental overage. Datadog grows as customers expand public/private cloud workloads. As of 31 Dec 2025: ~4,310 customers with ARR ≥ $100k (**90% of ARR**); NRR **~120%** from existing-customer usage; FY 2025 revenue **$3.43bn (+28%)**; RPO **$3.46bn**. NRR/RPO/large-customer counts are 10-K disclosures, not a quarterly Company Facts series.

| # | Dataset | Measure + source | Logic + evidence | Freq / lag / cost | Limits |
|---|---|---|---|---|---|
| 1 | **npm** (one source; two packages) | `@datadog/browser-rum` and `dd-trace` daily downloads. Public npm API. | 10-K usage/expansion. Instrumentation proxy. Counts are HTTP-200 tarball hits incl. CI (npm 2014; Dey & Mockus 2018). **Own check:** RUM 0.86 coincident / 0.69 lag 1; `dd-trace` 0.55 / 0.22. | Daily; ~1-day; **free** | CI/mirrors. ≥85% coverage. Not two sources. |
| 2 | **Hyperscaler cloud XBRL** (one source) | AWS, Google Cloud, MSFT Intelligent Cloud **revenue** from SEC XBRL segment members. | 10-K: DDOG grows with public-cloud workloads. **Macro control**, **not high-frequency**, not DDOG accounts. **Own check:** AWS 0.78 coincident / **0.78 lag 1** (n=14). GCP 0.95 coincident (n=12) is AI-regime coincidence. | Quarterly on filing; **free SEC** | Not account-level. MSFT FY ≠ calendar. |
| 3 | **Wikimedia pageviews** | Official API, “Datadog”; New Relic placebo. Trends **not** used (no official public API). Choi & Varian (2012) support search *nowcasts*; Da et al. (2011) is ticker attention. | ToS-safe attention proxy. **Own check:** Wiki DDOG −0.09 coincident; 0.76 at lag 2 (fragile). New Relic wiki **negative**. | Monthly API; **free official** | Empirically weak coincident. Never equate views with paid usage. |
| 4 | Hiring / skills | Licensed job-post vendor. **Not ingested.** | Gutiérrez et al. (2020): job-post changes associate with **future** sales. | Paid — do not scrape | Proposed only. |

**Count:** 3 ingested + 1 proposed (still in the 3–5 band). npm is not two sources. Cloud is not an HF Datadog signal.

## 2. Methodology

**Target.** Quarterly DDOG revenue YoY from SEC Company Facts (`CIK0001561550`). Q4 = FY − (Q1+Q2+Q3), flagged `q4_derived_from_fy`.

**Signals.** npm: 180-day chunks, same-quarter YoY, ≥85% daily coverage. **Intra-quarter stub:** sum downloads from quarter start through `as_of` vs the same day-of-quarter window one year prior. Cloud: duration XBRL (80–102 days); YTD dropped. Wiki: three months per quarter.

**Sample.** 2023Q1–2026Q2 (14 quarters). Stub backtest uses the same day-of-quarter as 2026-09-02 on each completed quarter.

**Lead–lag.** Pearson of calendar-lagged signal YoY vs revenue YoY. Lag 0 = **coincident nowcast**. Lag 1 = the validated call.

**Model.** Standardized ridge (α=10) on lag-1 RUM and lag-1 `dd-trace`. Expanding window, min 6 train, 8 OOS. Controls: +lag-1 AWS, +lag-1 wiki. Baseline: **persistence**. Optional walk-forward adds same-quarter stub features **known as of the stub date** (no post-print leak). Primary **call** stays lag-1 npm.

**Guidance baseline.** No Street vendor. Q3 2026 company outlook from EDGAR 8-K Exhibit 99.1 (6 Aug 2026): revenue **$1.135–1.145bn**.

## 3. Findings

**Lead–lag (2023Q1–2026Q2)**

| Signal | Lag 0 | Lag 1 | Lag 2 | n (lag 0) |
|---|---|---|---|---|
| RUM YoY | **0.860** | 0.694 | 0.425 | 14 |
| `dd-trace` YoY | **0.550** | 0.222 | 0.204 | 14 |
| AWS YoY | 0.778 | **0.783** | 0.646 | 14 |
| GCP YoY | **0.953** | 0.895 | 0.727 | 12 |
| Wiki Datadog YoY | −0.087 | 0.297 | **0.757** | 14 |
| Wiki New Relic YoY | −0.354 | −0.373 | −0.460 | 14 |

RUM is a **coincident nowcast** with a weaker one-quarter lead. AWS **leads as much as it coincides** — cloud-spend regime, not a DDOG usage meter. GCP 0.95 (smaller n; 2026Q2 GCP +82% vs DDOG +36%) is AI-infra co-movement. Wiki is not a nowcast.

**Walk-forward (8 forecasts, 2024Q3–2026Q2)**

| Model | RMSE | MAPE | Change hit |
|---|---|---|---|
| Ridge (npm lag-1) | 0.033 | 0.089 | 0.13 |
| Ridge (npm + AWS lag-1) | 0.026 | 0.082 | 0.13 |
| Ridge (npm lag-1 + coincident stub) | 0.026 | 0.071 | 0.25 |
| Persistence | **0.021** | **0.054** | 0.00 |

Sign hit is 1.00 because growth stayed positive. npm+AWS and lag-1+stub both **improve** the ridge; **neither beats persistence**. Latest print: **$1,121m**, **35.6%** YoY (2026Q2). Lag-1 npm missed the 2026 acceleration (actual 35.6% vs ridge 28.6% in 2026Q2).

**Intra-quarter stub (2026Q3 as of 2026-09-02).** Coverage **70%** (64/92 days). RUM stub YoY **+139%** vs last full-quarter RUM **+111%** (still accelerating at the package layer). `dd-trace` stub **+138%** vs last full **+98%**. Backtest: RUM stub vs eventual revenue YoY corr **0.87** (n=14) — **coincident**, similar to full-quarter RUM 0.86; it does **not** lead earnings. Stub npm YoY is not on a revenue scale; do not read +139% as a 139% revenue call.

**Baselines for 2026Q3 revenue YoY.** Persistence / last print **35.6%**. Lag-1 ridge **30.6%**. Management guidance midpoint **28.7%** ($1.140bn / 2025Q3 $886m). Tracker is **behind** last print and **above** the company outlook midpoint.

**What the data support.** (1) RUM tracks reported growth as a nowcast. (2) AWS is a coincident/lag-1 cloud control and helps the ridge. (3) Intra-quarter npm is a usable coincident update; adding it still loses to persistence. (4) Wiki/Trends-style attention is not a coincident nowcast. (5) Persistence still wins.

**What they do not support.** Causal claims, stock recommendations, that npm *is* usage, that the stub leads the print, that GCP’s 0.95 is DDOG-specific, or that hiring was tested.

## 4. Dashboard prototype

Working UI: annotated Vite (`cd dashboard && npm run dev`, or `npm --prefix dashboard run build`). Streamlit is an optional Python fallback.

- **Header:** generated timestamp; refresh = re-run `python src/analyze_ddog.py` then rebuild.  
- **KPIs + stub strip:** last print, lag-1 ridge (**validated model**), coincident npm stub (**small sample**), management guidance.  
- **Charts / lead–lag / walk-forward** vs persistence. Cloud is a **control**, not the call.

## 5. Limitations and next tests

Small *n*; npm CI inflation; Q4 residual; GCP/MSFT gaps; wiki news spikes; no Street consensus (company 8-K only). Production: licensed hiring, placebo non-Datadog npm, residual vs AWS with a longer sample. Until then, a research tracker with persistence and disclosed guidance as baselines.

## References

1. Datadog 2025 Form 10-K: https://www.sec.gov/Archives/edgar/data/1561550/000162828026008819/ddog-20251231.htm  
2. Datadog usage details: https://docs.datadoghq.com/account_management/plan_and_usage/usage_details.md  
3. npm download-counts API: https://github.com/npm/download-counts  
4. npm (2014), numeric precision / download counts: https://blog.npmjs.org/post/92574016600/numeric-precision-matters-how-npm-download-counts-work.html  
5. SEC Company Facts: https://data.sec.gov/api/xbrl/companyfacts/CIK0001561550.json  
6. SEC EDGAR XBRL (AMZN AWS, GOOG Cloud, MSFT Intelligent Cloud)  
7. Wikimedia pageviews API: https://wikimedia.org/api/rest_v1/  
8. Dey, T. & Mockus, A. (2018). PROMISE. https://doi.org/10.1145/3273934.3273942  
9. Gutiérrez, E. et al. (2020). *Management Science* 66(7). https://doi.org/10.1287/mnsc.2019.3450  
10. Choi, H. & Varian, H. (2012). *Economic Record* 88(s1). https://doi.org/10.1111/j.1475-4932.2012.00809.x  
11. Da, Z., Engelberg, J. & Gao, P. (2011). *Journal of Finance* 66(5). https://doi.org/10.1111/j.1540-6261.2011.01679.x  
12. Datadog 8-K Exhibit 99.1, 6 Aug 2026 (Q3 2026 outlook): https://www.sec.gov/Archives/edgar/data/1561550/000162828026053829/ex-991x20260630x8k.htm  
