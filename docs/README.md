# Documentation

Public-data pre-earnings tracker for Datadog (NASDAQ: DDOG). Research aid only — not investment advice.

## Start here

| Doc | Markdown | Word (`.docs`) |
|---|---|---|
| Report | [report.md](report.md) | [report.docs](report.docs) |
| Presentation | [presentation.md](presentation.md) | [presentation.docs](presentation.docs) |
| Dashboard | [dashboard.md](dashboard.md) | [dashboard.docs](dashboard.docs) |
| Runbook | [runbook.md](runbook.md) | [runbook.docs](runbook.docs) |
| Technical design | [technical-design.md](technical-design.md) | [technical-design.docs](technical-design.docs) |
| Slides | [slides.html](slides.html) | — (HTML only) |

Each `.docs` file is a Word-compatible document (Office Open XML). Rename to `.docx` if your editor expects that extension. Regenerate after editing markdown: `./scripts/export_docs.sh`

## Headline numbers (2026Q3)

- Last print: **$1,121m / 35.6% YoY** (2026Q2)
- Lag-1 ridge call: **30.6%** — tracking **behind** last print (±1pp rule)
- Company 8-K midpoint: **~28.7%** implied YoY
- Intra-quarter RUM stub: **+151%** package YoY through **2026-09-01** (63/92 days) — coincident, not a revenue forecast
- Walk-forward RMSE: persistence **2.1pp**, npm ridge **3.3pp**, npm+AWS **2.6pp**

## Quick run

```bash
chmod +x scripts/*.sh
./scripts/setup.sh && ./scripts/analyze.sh && ./scripts/test.sh && ./scripts/dashboard.sh
```

Live demo: https://ddog-earnings-tracker.vercel.app/
