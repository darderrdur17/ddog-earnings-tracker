# Datadog alternative data take-home — submission packet

**Candidate deliverables mapped to assignment requirements.**

## 1. Written report (max 5 pages)

| Format | Path |
|---|---|
| Markdown (source) | [`docs/report.md`](docs/report.md) |
| Word | [`docs/report.docs`](docs/report.docs) (rename to `.docx` if needed) |
| Copy at zip root | `report.md`, `report.docs` |

Covers: data selection and rationale, methodology, statistical findings, limitations, references.

## 2. Ten-slide deck (alternative to long report)

| Path | Notes |
|---|---|
| [`docs/slides.html`](docs/slides.html) | Open in any browser; arrow keys to navigate |
| Copy at zip root | `slides.html` |
| Live + dashboard | https://ddog-earnings-tracker.vercel.app/slides.html |

Speaker script: [`docs/presentation.md`](docs/presentation.md)

## 3. Dashboard prototype with annotations

| Path | Notes |
|---|---|
| [`dashboard/`](dashboard/) | Annotated React/Vite working prototype |
| [`docs/dashboard.md`](docs/dashboard.md) | Section-by-section walkthrough |
| Live demo | https://ddog-earnings-tracker.vercel.app/ |

Shows: update cadence, lag-1 revenue call vs last print / 8-K, ahead/behind rule (±1pp), lead–lag, walk-forward vs persistence, source links.

## 4. Code (optional)

| Path | Notes |
|---|---|
| [`src/`](src/) | Python collectors, features, ridge walk-forward |
| [`tests/`](tests/) | 22 pytest tests |
| [`scripts/`](scripts/) | Setup, analyze, test, dashboard, zip |
| [`data/`](data/) | Cached public-source CSVs |
| [`outputs/`](outputs/) | Analysis tables and `analysis_summary.json` |

## Reproduce locally

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/analyze.sh   # refresh from public APIs (optional if data/ present)
./scripts/test.sh
./scripts/dashboard.sh # http://127.0.0.1:5173
```

Full runbook: [`docs/runbook.md`](docs/runbook.md)

## Data compliance

Public SEC Company Facts, EDGAR XBRL, npm downloads API, Wikimedia pageviews API only. No Google Trends scrape, no job-board scrape, no MNPI. Research aid — not investment advice.

## Doc index

[`docs/README.md`](docs/README.md)
