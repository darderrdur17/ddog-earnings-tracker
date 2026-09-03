# Dashboard guide

The annotated Vite app is the working prototype — read it top to bottom the way an analyst would.

## Run locally

```bash
./scripts/dashboard.sh
```

Open http://127.0.0.1:5173. Slides: http://127.0.0.1:5173/slides.html

Production build: `./scripts/build.sh` then `./scripts/preview.sh` (http://127.0.0.1:4173).

Live demo: https://ddog-earnings-tracker.vercel.app/

Streamlit is an optional Python fallback (`./scripts/streamlit.sh`) — not the interview surface.

## Layout (top to bottom)

1. **Header** — Generated timestamp, refresh commands, link to slides.
2. **KPI row** — Last print ($1,121m / 35.6% YoY), lag-1 ridge call (30.6%), company 8-K midpoint (~28.7%). Ahead/behind uses ±1pp versus last reported YoY, not Street consensus.
3. **Intra-quarter stub strip** — npm package YoY through the latest settled day (2026-09-01, 63/92 days). Labeled **coincident** — not a revenue forecast.
4. **Growth charts** — Reported revenue YoY vs npm and cloud signals over 14 quarters.
5. **Call construction** — How the lag-1 ridge is built; what is in and out of the validated call.
6. **Lead–lag table** — Pearson correlations by calendar lag.
7. **Walk-forward vs persistence** — Eight out-of-sample forecasts; RMSE comparison.
8. **Sources and limits** — Freshness, public URLs, caveats.

## Refresh data

```bash
./scripts/analyze.sh
./scripts/build.sh   # if serving a static build
```

Analysis writes `outputs/analysis_summary.json` and syncs into the dashboard via `scripts/sync_dashboard_summary.py`.

## What to say in a demo

- RUM **nowcasts** reported growth (0.86 coincident) — it is not a strong *lead*.
- The **stub** (+151% package YoY) is a same-quarter download update, not a revenue call.
- **Persistence** (2.1pp RMSE) beats the ridge — that is a feature, not a bug.
- Every number links back to a public source or a stated formula.
