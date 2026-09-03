# Alternative data research: Datadog (NASDAQ: DDOG)

**Take-home assignment** · 3 September 2026  
Public SEC, npm, and Wikimedia data only. Hiring was not scraped. Research tracker — not investment advice.

The dashboard is the working prototype. The slide deck is the talk track. This note is the scored write-up.

## The short version

I went looking for *leading* indicators of Datadog’s quarterly revenue growth. On public data, the honest answer is more modest than that.

Datadog’s 2025 10-K describes the engine: mostly annual subscriptions, committed usage (recognized ratably or as used) plus monthly usage and overage, growth as customers expand cloud workloads. About 90% of ARR sits with customers ≥ $100k; NRR is ~120% from existing-customer usage; year-end RPO was $3.46bn. Those NRR / RPO / large-customer figures are annual disclosures — not a quarterly Company Facts series I can nowcast. So I used **revenue YoY** as the target and looked for activity that should move with usage and cloud expansion.

Three sources were ingested (npm, hyperscaler XBRL, Wikimedia) and one was proposed only (hiring). `@datadog/browser-rum` **nowcasts** reported growth: 0.86 coincident, 0.69 one quarter ahead. AWS segment YoY is a **cloud-regime control** (0.78 coincident and 0.78 at lag 1), not a Datadog meter. Adding lag-1 AWS to a simple npm ridge cuts eight-quarter RMSE from 3.3pp to 2.6pp. Persistence is still better, at 2.1pp. Wikipedia “Datadog” pageviews do not nowcast (−0.09 coincident).

**2026Q3 call (lag-1 ridge, signals through 2026Q2): 30.6% revenue YoY**, versus last print **35.6%** — tracking behind. Intra-quarter npm through **1 September 2026** (63 of 92 days) is still accelerating at the *package* layer (RUM **+151%** YoY vs the same Jul 1–Sep 1 window in 2025). That is a coincident download update, not a 151% revenue forecast. Company 8-K outlook is $1.135–1.145bn, about **28.2–29.3%** implied YoY. The ridge sits between last print and management’s midpoint.

I would rather show that persistence wins than dress a weaker model as alpha.

## Data selection

For each source: what it measures, why it should map to Datadog’s model, update cadence, cost, and where it sits in the stack.

**npm downloads — one source, two packages.** Daily counts for `@datadog/browser-rum` and `dd-trace` from the public npm API. These are HTTP-200 tarball hits, including CI (npm, 2014; Dey & Mockus, 2018) — an instrumentation / adoption proxy, not billable usage. The 10-K usage-and-expansion story is the economic link: more instrumented workloads should eventually show up in committed usage and overage. Own check: RUM 0.86 coincident / 0.69 lag 1; `dd-trace` 0.55 / 0.22. Daily, ~one-day lag, free. Limits: CI inflation, mirrors, coverage floor of 85% of days in a quarter. Counting two packages as two *sources* would be cheating.

**Hyperscaler cloud XBRL — one source, three members.** AWS, Google Cloud, and Microsoft Intelligent Cloud segment *revenue* from SEC XBRL. The 10-K says Datadog grows with public-cloud workloads and sells through those clouds. That is a **macro control**, not high-frequency Datadog telemetry and not account-level attach. Own check: AWS 0.78 coincident / 0.78 lag 1 (n=14). GCP 0.95 coincident (n=12) is too tidy — 2026Q2 GCP +82% versus Datadog +36% looks like an AI-infra regime, not Datadog-specific demand. Quarterly on filing, free. Limits: not HF; Microsoft’s fiscal year is not calendar.

**Wikimedia pageviews.** Official API, “Datadog,” with New Relic as a placebo. Choi & Varian (2012) support search *nowcasts*; Da et al. (2011) is ticker attention. I did not scrape Google Trends (no official public API I was willing to use). Own check: Wiki Datadog −0.09 coincident; 0.76 at lag 2 (fragile); New Relic wiki is negative, so this is not “observability traffic” in general. Monthly, free, ToS-safe. Empirically a weak coincident series. Pageviews are not paid usage.

**Hiring / skills — proposed, not ingested.** Gutiérrez et al. (2020) find job-post changes associate with *future* sales. Job boards’ terms forbid scraping, so this stays a licensed-vendor idea (LinkUp, Revelio, Thinknum). Still inside the 3–5 source band: 3 ingested + 1 proposed.

## Methodology

**Target.** Quarterly Datadog revenue YoY from SEC Company Facts (`CIK0001561550`). When a Q4 frame is missing, Q4 = FY − (Q1+Q2+Q3), flagged in the panel.

**Features.** npm is pulled in 180-day chunks, summed to the calendar quarter, YoY only if coverage ≥ 85%. Intra-quarter **stub**: downloads from quarter start through `as_of`, versus the same day-of-quarter window a year earlier. Trailing npm days that still read as 0 (unsettled API) are dropped from `as_of` so we do not compare an incomplete current window to a complete prior-year window. Cloud uses duration XBRL (~80–102 days); year-to-date contexts are dropped. Wiki needs three months in the quarter.

**Sample.** 2023Q1–2026Q2, 14 complete YoY quarters. Stub backtests reuse the 1 September 2026 day-of-quarter offset on each completed quarter.

**Lead–lag.** Pearson correlation of calendar-lagged signal YoY with revenue YoY. Lag 0 is a coincident nowcast. Lag 1 is the validated call. A row shift across a missing quarter is not a lag.

**Model.** Standardized ridge (α = 10) on lag-1 RUM and lag-1 `dd-trace`. Expanding window, at least six training quarters, eight out-of-sample forecasts. Ablations add lag-1 AWS and/or the coincident stub *known as of the stub date*. Baseline is last quarter’s growth (**persistence**). No Street scrape; Q3 2026 company outlook is EDGAR 8-K Exhibit 99.1 (6 August 2026), $1.135–1.145bn. The published call uses lag-1 npm only — same-quarter downloads do not leak into that number.

## Findings

**Lead–lag (2023Q1–2026Q2)**

| Signal | Lag 0 | Lag 1 | Lag 2 | n (lag 0) |
|---|---|---|---|---|
| RUM YoY | **0.860** | 0.694 | 0.425 | 14 |
| `dd-trace` YoY | **0.550** | 0.222 | 0.204 | 14 |
| AWS YoY | 0.778 | **0.783** | 0.646 | 14 |
| GCP YoY | **0.953** | 0.895 | 0.727 | 12 |
| Wiki Datadog YoY | −0.087 | 0.297 | **0.757** | 14 |
| Wiki New Relic YoY | −0.354 | −0.373 | −0.460 | 14 |

RUM is a coincident nowcast with a weaker one-quarter lead. I would not call lag 0 a leading indicator. AWS leads about as much as it coincides — that is cloud spend, not Datadog seats. GCP’s 0.95 sits on a shorter sample and a 2026 AI-capex boom. Wiki is not a nowcast; the lag-2 spike is the kind of pattern you do not bet a quarter on.

**Walk-forward (eight forecasts, 2024Q3–2026Q2)**

| Model | RMSE | MAPE | Change-direction hit |
|---|---|---|---|
| Ridge (npm lag-1) | 0.033 | 0.089 | 0.13 |
| Ridge (npm + AWS lag-1) | 0.026 | 0.082 | 0.13 |
| Ridge (npm lag-1 + coincident stub) | 0.026 | 0.071 | 0.25 |
| Persistence | **0.021** | **0.054** | 0.00 |

Sign-of-growth hit is 1.00 because every print in the window was still positive — that is not timing skill. AWS and the stub both *help* the ridge. Neither beats “last quarter’s growth again.” Latest print: **$1,121m**, **35.6%** YoY (2026Q2). Lag-1 npm missed the 2026 acceleration (actual 35.6% versus ridge 28.6% in 2026Q2). That miss is the story, not a footnote.

**Intra-quarter stub (2026Q3 as of 2026-09-01).** Coverage 68% (63/92 days). RUM stub YoY **+151%** versus last full-quarter RUM **+111%**; `dd-trace` stub **+149%** versus **+98%**. Package downloads are still running hot versus last quarter. Backtest: RUM stub versus *eventual* revenue YoY corr **0.86** (n=14) — coincident, in line with full-quarter RUM, **not a lead**. Do not read +151% as a revenue call; the scales are different.

**2026Q3 stack.** Persistence 35.6%. Lag-1 ridge **30.6%** (behind by 5.1pp under a ±1pp rule versus last print, not versus Street). 8-K midpoint **28.7%**. Tracker is behind the print and a little above management’s midpoint.

**What this supports.** RUM tracks reported growth as a nowcast. AWS is a useful coincident / lag-1 cloud control. Intra-quarter npm is a fair coincident update. Attention (wiki / Trends-style) is not a coincident nowcast here. Persistence is still the RMSE champion.

**What it does not support.** Causality, a stock view, “npm equals usage,” “the stub leads the print,” “GCP 0.95 is Datadog-specific,” or any claim that hiring was tested.

## Dashboard

See [dashboard.md](dashboard.md) for the UI walkthrough. Live demo: https://ddog-earnings-tracker.vercel.app/

## Limitations and next steps

Fourteen quarters is a small sample. npm includes CI. Q4 is sometimes a residual. GCP and Microsoft have gaps. Wiki jumps on news. There is no Street consensus in this packet — only the company 8-K. Production would license hiring, add a non-Datadog npm placebo, and watch one full earnings cycle with the stub held fixed before the print. Until then this is a cited research tracker: persistence and disclosed guidance as baselines, and a model that is allowed to lose.

## References

1. Datadog 2025 Form 10-K: https://www.sec.gov/Archives/edgar/data/1561550/000162828026008819/ddog-20251231.htm  
2. Datadog usage details: https://docs.datadoghq.com/account_management/plan_and_usage/usage_details.md  
3. npm download-counts API: https://github.com/npm/download-counts  
4. npm (2014), how download counts work: https://blog.npmjs.org/post/92574016600/numeric-precision-matters-how-npm-download-counts-work.html  
5. SEC Company Facts: https://data.sec.gov/api/xbrl/companyfacts/CIK0001561550.json  
6. SEC EDGAR XBRL (AMZN AWS, GOOG Cloud, MSFT Intelligent Cloud)  
7. Wikimedia pageviews API: https://wikimedia.org/api/rest_v1/  
8. Dey, T. & Mockus, A. (2018). PROMISE. https://doi.org/10.1145/3273934.3273942  
9. Gutiérrez, E. et al. (2020). *Management Science* 66(7). https://doi.org/10.1287/mnsc.2019.3450  
10. Choi, H. & Varian, H. (2012). *Economic Record* 88(s1). https://doi.org/10.1111/j.1475-4932.2012.00809.x  
11. Da, Z., Engelberg, J. & Gao, P. (2011). *Journal of Finance* 66(5). https://doi.org/10.1111/j.1540-6261.2011.01679.x  
12. Datadog 8-K Exhibit 99.1, 6 Aug 2026 (Q3 2026 outlook): https://www.sec.gov/Archives/edgar/data/1561550/000162828026053829/ex-991x20260630x8k.htm  
