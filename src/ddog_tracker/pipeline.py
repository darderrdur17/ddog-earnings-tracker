from __future__ import annotations

import json
import math
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

from .collectors.npm_downloads import fetch_npm_package
from .collectors.sec_revenue import fetch_sec_revenue
from .collectors.sec_segment import fetch_all_cloud_segments
from .collectors.wiki_pageviews import fetch_wiki_article
from .config import Settings, default_settings
from .features import (
    aggregate_monthly_quarterly,
    aggregate_npm_quarterly,
    build_panel,
    lead_lag_table,
    quarterly_yoy_frame,
    shift_by_calendar_quarters,
)
from .http_client import JsonHttpClient
from .intra_quarter import build_intra_quarter, sync_dashboard_summary
from .model import latest_estimate, walk_forward


def run(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or default_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.out_dir.mkdir(parents=True, exist_ok=True)
    client = JsonHttpClient(settings)

    revenue = fetch_sec_revenue(client, settings)
    revenue.to_csv(settings.data_dir / "ddog_sec_revenue.csv", index=False)

    extras: list[pd.DataFrame] = []
    npm_labels: list[str] = []
    npm_dailies: dict[str, pd.DataFrame] = {}
    for package, label in settings.npm_packages:
        daily = fetch_npm_package(client, settings, package, label)
        daily.to_csv(settings.data_dir / f"npm_{label}_daily.csv", index=False)
        npm_dailies[label] = daily
        extras.append(
            aggregate_npm_quarterly(daily, label, settings.min_quarter_coverage)
        )
        npm_labels.append(label)

    cloud_labels: list[str] = []
    for frame in fetch_all_cloud_segments(client, settings):
        value_col = [c for c in frame.columns if c.endswith("_revenue")][0]
        labeled = quarterly_yoy_frame(frame, value_col)
        labeled.to_csv(settings.data_dir / f"cloud_{value_col}.csv", index=False)
        extras.append(labeled)
        cloud_labels.append(value_col)

    wiki_labels: list[str] = []
    for article, label in settings.wiki_articles:
        monthly = fetch_wiki_article(client, settings, article, label)
        monthly.to_csv(settings.data_dir / f"wiki_{label}_monthly.csv", index=False)
        extras.append(aggregate_monthly_quarterly(monthly, label, min_coverage=1.0))
        wiki_labels.append(label)

    required_complete = [f"{label}_complete" for label in npm_labels]
    panel = build_panel(revenue, extras, required_complete_cols=required_complete)

    npm_yoy = [f"{label}_yoy" for label in npm_labels]
    cloud_yoy = [f"{label}_yoy" for label in cloud_labels]
    wiki_yoy = [f"{label}_yoy" for label in wiki_labels]
    all_yoy = npm_yoy + cloud_yoy + wiki_yoy

    for col in all_yoy:
        if col in panel.columns:
            panel[f"{col}_lag1"] = shift_by_calendar_quarters(
                panel[col], panel["quarter"], 1
            )

    npm_lag = [f"{c}_lag1" for c in npm_yoy]
    aws_lag = [c for c in panel.columns if c == "aws_revenue_yoy_lag1"]
    wiki_ddog_lag = [c for c in panel.columns if c == "wiki_datadog_views_yoy_lag1"]
    control_lag = npm_lag + aws_lag + wiki_ddog_lag

    modeled = panel[panel["quarter"] >= settings.analysis_start_quarter].reset_index(
        drop=True
    )
    lead_lag = lead_lag_table(
        panel, all_yoy, start_quarter=settings.analysis_start_quarter
    )
    predictions, metrics = walk_forward(modeled, npm_lag, settings)
    _, rum_metrics = walk_forward(
        modeled, [c for c in npm_lag if "browser_rum" in c], settings
    )
    metrics["ridge_rum_lag1_only"] = rum_metrics.get("ridge", {})
    if aws_lag:
        _, aws_metrics = walk_forward(modeled, npm_lag + aws_lag, settings)
        metrics["ridge_npm_aws_lag1"] = aws_metrics.get("ridge", {})
    if wiki_ddog_lag:
        _, wiki_metrics = walk_forward(modeled, npm_lag + wiki_ddog_lag, settings)
        metrics["ridge_npm_wiki_lag1"] = wiki_metrics.get("ridge", {})
    if len(control_lag) > len(npm_lag):
        _, both_metrics = walk_forward(modeled, control_lag, settings)
        metrics["ridge_npm_aws_wiki_lag1"] = both_metrics.get("ridge", {})

    estimate = latest_estimate(modeled, npm_lag, npm_yoy, settings)
    npm_as_of = date.today()
    intra = build_intra_quarter(
        npm_dailies, modeled, estimate, settings, npm_as_of, npm_lag
    )

    panel.to_csv(settings.out_dir / "model_panel.csv", index=False)
    lead_lag.to_csv(settings.out_dir / "lead_lag.csv", index=False)
    pred_out = predictions.drop(columns=["contributions"], errors="ignore")
    pred_out.to_csv(settings.out_dir / "walk_forward_predictions.csv", index=False)

    as_of = datetime.now(timezone.utc).isoformat()
    chart_panel = _chart_panel(modeled)
    walk_rows = pred_out.to_dict("records")
    summary = {
        "as_of_utc": as_of,
        "generated_at_utc": as_of,
        "refresh_instructions": (
            "Re-run `python src/analyze_ddog.py` then "
            "`npm --prefix dashboard run build` (or `npm run dev`)."
        ),
        "npm_end": npm_as_of.isoformat(),
        "sample_quarters": int(modeled["revenue_yoy"].notna().sum()),
        "joined_complete_quarters": int(
            modeled["signals_complete"].fillna(False).sum()
        ),
        "analysis_start_quarter": settings.analysis_start_quarter,
        "panel_quarters": panel["quarter"].tolist(),
        "model_quarters": modeled["quarter"].tolist(),
        "signals": npm_labels + cloud_labels + wiki_labels,
        "feature_cols": npm_lag,
        "control_feature_cols": control_lag,
        "lead_lag": lead_lag.to_dict("records"),
        "best_leads": _best_leads(lead_lag),
        "walk_forward": metrics,
        "walk_forward_rows": walk_rows,
        "latest_estimate": estimate,
        "intra_quarter": intra,
        "chart_panel": chart_panel,
        "sources": {
            "sec": settings.sec_url,
            "npm": "https://api.npmjs.org/downloads/range/",
            "sec_xbrl": "https://www.sec.gov/Archives/edgar/data/",
            "wikimedia": "https://wikimedia.org/api/rest_v1/metrics/pageviews/",
        },
        "caveat": (
            "npm downloads are developer-adoption proxies, not Datadog billable "
            "usage. AWS/Google Cloud/MSFT Intelligent Cloud are official SEC XBRL "
            "segment revenues (macro controls, not DDOG accounts). Wikipedia "
            "pageviews are an official attention API, not Google Trends and not "
            "paid usage. Q4 DDOG revenue is FY minus Q1–Q3. Hiring is not ingested "
            "(licensed boards only). Results are exploratory, not investment advice."
        ),
    }
    payload = _json_safe(summary)
    (settings.out_dir / "analysis_summary.json").write_text(
        json.dumps(payload, indent=2, default=_json_default, allow_nan=False)
    )
    sync_dashboard_summary(settings)
    print(json.dumps(payload, indent=2, default=_json_default, allow_nan=False))
    return summary


def _chart_panel(modeled: pd.DataFrame) -> list[dict[str, Any]]:
    cols = [
        "quarter",
        "revenue",
        "revenue_yoy",
        "browser_rum_downloads_yoy",
        "dd_trace_downloads_yoy",
        "aws_revenue_yoy",
        "gcp_revenue_yoy",
        "msft_ic_revenue_yoy",
        "wiki_datadog_views_yoy",
        "wiki_newrelic_views_yoy",
    ]
    keep = [c for c in cols if c in modeled.columns]
    rows = modeled[keep].where(pd.notna(modeled[keep]), None)
    return rows.to_dict("records")


def _best_leads(lead_lag: pd.DataFrame) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for signal, group in lead_lag.groupby("signal"):
        ranked = group.dropna(subset=["corr"]).sort_values("corr", ascending=False)
        if ranked.empty:
            continue
        top = ranked.iloc[0]
        out[str(signal)] = {
            "lag_quarters": int(top["lag_quarters"]),
            "corr": float(top["corr"]),
            "n": int(top["n"]),
        }
    return out


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if pd.isna(value):
        return None
    return value


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, float):
        return value
    return str(value)
