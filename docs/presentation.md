# 10-slide talk (15 minutes + 5 Q&A)

Speaker script for [slides.html](slides.html) — also at `/slides.html` on the dashboard. Scored write-up: [report.md](report.md).

**Numbers as of 8 September 2026.** npm is settled through **6 Sep** (68/92 days of 2026Q3). Demo the Vite app, not Streamlit: `./scripts/dashboard.sh` → http://127.0.0.1:5173

Say it like a research conversation, not a pitch. Pause after the three headline numbers on slide 1.

---

## Slide 1 — What we are actually deciding (1:00)

“Thanks — I’ll keep this to about fifteen minutes, then we can open the dashboard.

The question I took from the brief is pretty specific. Not ‘can I beat the Street,’ and not a stock view. It’s: can an analyst see Datadog *activity* before the print, with the sources and the uncertainty still on the page?

Here’s the stack as of yesterday’s packet. Last print, 2026Q2, is **$1,121m, 35.6% YoY**. The lag-1 ridge call for 2026Q3 is **30.6%** — that uses signals only through Q2, so it doesn’t leak this quarter’s downloads. Company 8-K midpoint is about **28.7%**. Under a ±1pp rule versus last print, we are tracking **behind**.

Walk-forward, persistence still wins. I’m going to show that on purpose. I’d rather be honest about a weaker model than dress it up as alpha.”

## Slide 2 — Why Datadog (1:15)

“Quickly, why this ticker maps to alternative data at all.

The 2025 10-K is pretty clear: mostly annual subscriptions, committed usage recognized ratably or as used, plus monthly usage and overage. About 90% of ARR sits with customers at or above $100k. NRR is around 120%, driven by existing-customer usage. Year-end RPO was $3.46bn. They grow as customers expand cloud workloads, and they sell through AWS, Azure, and GCP.

One important limit: NRR, RPO, and the large-customer counts are *annual* disclosures. They’re not a quarterly Company Facts series I can nowcast. So the target in this packet is **revenue YoY**. Everything else is a story we test, not a second target we pretend to forecast.”

## Slide 3 — Sources (1:30)

“Three sources ingested, one proposed. That keeps us inside the 3–5 band without cheating.

**npm** is one source, two packages: `@datadog/browser-rum` and `dd-trace`. Daily public API. These are tarball hits, including CI, so this is an instrumentation / adoption proxy — not billable usage. The 10-K usage-and-expansion story is the economic link.

**Hyperscaler XBRL** is one source, three members — AWS, Google Cloud, Microsoft Intelligent Cloud. That’s a cloud-regime *control*, not a Datadog meter and not account-level attach.

**Wikipedia** ‘Datadog’ pageviews, with New Relic as a placebo. ToS-safe attention. I didn’t scrape Google Trends — no official public API I was willing to use.

**Hiring** I would love, and the Gutiérrez et al. paper supports the logic. Job boards’ terms forbid scraping, so it stays licensed-vendor only. I didn’t pretend I ingested it.”

## Slide 4 — Method (1:15)

“Method is intentionally simple, because we only have fourteen complete YoY quarters, 2023Q1 through 2026Q2.

Target is SEC revenue YoY. When Q4 is missing as a frame, it’s FY minus Q1 through Q3, and that’s flagged.

Lead–lag is calendar-matched, not a naive row shift. The **validated call** is ridge on lag-1 npm only — RUM and dd-trace, no same-quarter downloads in that number.

The **stub** is a coincident update: downloads from quarter start through the last settled npm day, versus the same day-of-quarter window a year earlier. As of this packet that’s **6 September**, 68 of 92 days. Trailing zeros on the npm API get dropped so we don’t compare an incomplete window to a complete one last year.

Baselines are last quarter’s growth — persistence — and the company 8-K. No Street scrape. Expanding window, no future row in training.”

## Slide 5 — Lead–lag (1:30)

“This is the finding people sometimes over-sell, so I’ll be blunt.

RUM correlates **0.86** with revenue YoY in the *same* quarter. At lag 1 it’s **0.69**. That’s a nowcast with a weaker one-quarter lead. I would not call lag 0 a leading indicator.

AWS is 0.78 coincident *and* 0.78 at lag 1. That’s cloud spend moving, not Datadog seats. GCP’s 0.95 looks amazing until you notice n=12 and 2026Q2 GCP at +82% versus Datadog at +36% — that’s an AI-infra regime, not a Datadog-specific meter.

Wikipedia Datadog is **−0.09** coincident. New Relic wiki is negative, so this isn’t ‘observability traffic’ in general. Attention does not nowcast here.”

## Slide 6 — Walk-forward + stub (1:45)

“Eight out-of-sample forecasts, 2024Q3 through 2026Q2.

Persistence RMSE is **2.1pp**. npm lag-1 ridge is **3.3pp**. Add lag-1 AWS, or add the coincident stub, and you get to about **2.6pp**. Better than the plain ridge. Still loses to ‘last quarter’s growth again.’

The live call is **30.6%** versus **35.6%** last print — behind by 5.1pp. Management’s 8-K is 28.2–29.3% implied YoY, so the ridge sits between the print and guidance.

The **+143%** on the right is the RUM stub as of 6 Sep. Same calendar window versus last year at the *package* layer. Last full-quarter RUM was +111%, so downloads are still running hot versus last quarter. Please do not hear +143% as a revenue forecast. The scales are different. In the backtest the stub correlates about **0.87** with *eventual* revenue YoY — coincident, same idea as full-quarter RUM, not a lead.

And the miss matters: in 2026Q2 the ridge called 28.6% and the print was 35.6%. That’s the story, not a footnote.”

## Slide 7 — Live dashboard (3:00)

“Let me walk the screen the way an analyst would, top to bottom.

Timestamp and npm through-date first — you should see **6 Sep**. Then the call stack: last print, lag-1 ridge, 8-K. Ahead/behind is ±1pp versus last *reported* YoY, not versus Street.

Stub strip is labeled coincident. Then growth and signal charts, how the call is built, lead–lag, walk-forward versus persistence, sources.

If you only remember one UI thing: every number either has a public URL or a formula we stated.”

## Slide 8 — What shipped (1:00)

“What’s in the zip: Python collectors for SEC, XBRL, npm, Wikimedia; the ridge walk-forward; the stub; 22 tests; this annotated Vite dashboard.

What’s not in the zip, and I’m not claiming: a Next.js/tRPC production app, licensed hiring, or a consensus vendor. Streamlit exists as a fallback. The interview surface is Vite.”

## Slide 9 — Limits (1:00)

“Fourteen quarters is a small sample — that’s why persistence is the champion, not a rounding error. npm includes CI. Q4 is sometimes a residual. Wiki jumps on news, so it stays out of the call. No Street number in this packet, only the 8-K.

If this went to production I’d license hiring, add a non-Datadog npm placebo, and freeze the stub before one full print so we can see whether it actually helped in real time.”

## Slide 10 — Close (0:30)

“Start narrow, public, reproducible. Show the workflow. Show the uncertainty.

I’d rather be wrong with a cited persistence forecast and an 8-K baseline than look precise without one. Happy to take questions.”

---

## Likely Q&A (5:00)

**Why not ingest hiring?**
“Job boards’ terms forbid scraping, so I didn’t. Gutiérrez et al. 2020 is the research logic — job-post changes and *future* sales. Production would license LinkUp, Revelio, Thinknum, something like that. Counting a scrape I didn’t run would be worse than leaving it proposed.”

**Why not Google Trends?**
“No official public API I was willing to use. Wikimedia is the ToS-safe attention series. Empirically it does **not** nowcast DDOG revenue. That’s useful negative evidence.”

**Is Streamlit the product?**
“No. Demo is the Vite app. Streamlit is a Python fallback if someone wants to run everything in one language.”

**Does the stub lead earnings?**
“No. Coincident — about 0.87 versus eventual revenue YoY, n=14. Adding it to the ridge still loses to persistence. And +143% is package downloads, not 143% revenue growth.”

**How do you prevent leakage?**
“Calendar lags, expanding-window training, and the published call uses lag-1 npm only. Same-quarter downloads never enter that 30.6%. If I add the stub in an ablation, those features are only ones known as of the stub date.”

**NRR / RPO / $100k customers?**
“They’re in the 10-K, and they’re the economic story. They’re not a usable quarterly Company Facts series, so I didn’t nowcast them.”

**Why is persistence allowed to win?**
“Because the assignment asked for honest interpretation on a short sample. A well-validated simple baseline beating a fancier model is the result. I’d rather show that than hide it.”

**npm through 6 Sep, not 8 Sep?**
“The public npm API still reads zeros on the trailing days. We drop those so we don’t compare an incomplete current window to a complete prior-year window. 6 Sep is the last settled day in this packet.”
