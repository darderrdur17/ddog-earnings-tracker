"""Streamlit prototype for DDOG Earnings Tracker.

Run from project root: streamlit run src/dashboard.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "outputs/model_panel.csv"
LL = ROOT / "outputs/lead_lag.csv"
PREDS = ROOT / "outputs/walk_forward_predictions.csv"
SUMMARY = ROOT / "outputs/analysis_summary.json"

st.set_page_config(page_title="DDOG Earnings Tracker", layout="wide")
st.title("DDOG Earnings Tracker")
st.caption(
    "Public-data research aid — not investment advice. "
    "Signals refresh daily (npm) and with SEC filings; the model is quarterly."
)

if not PANEL.exists() or not SUMMARY.exists():
    st.error("Run `python3 src/analyze_ddog.py` first.")
    st.stop()

df = pd.read_csv(PANEL)
ll = pd.read_csv(LL)
summary = json.loads(SUMMARY.read_text())
preds = pd.read_csv(PREDS) if PREDS.exists() else pd.DataFrame()
estimate = summary.get("latest_estimate") or {}
walk = summary.get("walk_forward") or {}

start_q = summary.get("analysis_start_quarter", "2023Q1")
chart_df = df[df["quarter"] >= start_q] if "quarter" in df.columns else df
reported = df.dropna(subset=["revenue_yoy"])
latest = reported.iloc[-1] if not reported.empty else df.iloc[-1]
as_of = summary.get("as_of_utc", "unknown")

header = st.columns(6)
header[0].metric(
    "Latest reported revenue",
    f"${latest.revenue / 1e6:,.0f}m",
    help="SEC Company Facts; Q4 is FY residual when no Q4 frame exists.",
)
header[1].metric("Reported revenue YoY", f"{latest.revenue_yoy:.1%}")
header[2].metric(
    "Tracker estimate",
    f"{estimate['pred']:.1%}" if estimate else "n/a",
    delta=(
        f"{estimate.get('delta_vs_baseline', 0):+.1%} vs baseline"
        if estimate
        else None
    ),
)
tracking = str(estimate.get("tracking", "n/a")).replace("_", " ")
header[3].metric("Tracking vs baseline", tracking)
best = summary.get("best_leads") or {}
rum_lead = best.get("browser_rum_downloads_yoy") or {}
header[4].metric(
    "RUM coincident corr",
    f"{float(rum_lead['corr']):.2f}" if rum_lead else "n/a",
    help="Lag 0 (coincident nowcast). Stronger than lag-1; not a leading-indicator claim.",
)
header[5].metric("Model confidence", str(estimate.get("confidence", "exploratory")))

st.caption(
    f"Generated {as_of}. npm through {summary.get('npm_end')}. "
    f"Modeled from {summary.get('analysis_start_quarter')} "
    f"({summary.get('sample_quarters')} YoY revenue quarters). "
    "Refresh: re-run python src/analyze_ddog.py. "
    "RUM lag-0 is a coincident nowcast, not a leading indicator."
)

intra = summary.get("intra_quarter") or {}
if intra:
    stub_cols = st.columns(4)
    stub_cols[0].metric(
        "Lag-1 ridge (validated)",
        f"{intra.get('lag1_ridge_call', 0):.1%}"
        if intra.get("lag1_ridge_call") is not None
        else "n/a",
    )
    stub_cols[1].metric(
        "RUM stub YoY (coincident)",
        f"{intra['rum_stub_yoy']:.1%}" if intra.get("rum_stub_yoy") is not None else "n/a",
        help="Same-calendar-day npm window vs a year ago. Not a revenue forecast.",
    )
    stub_cols[2].metric(
        "dd-trace stub YoY",
        f"{intra['dd_trace_stub_yoy']:.1%}"
        if intra.get("dd_trace_stub_yoy") is not None
        else "n/a",
    )
    guide = intra.get("management_guidance") or {}
    if guide.get("available") and guide.get("implied_yoy_mid") is not None:
        stub_cols[3].metric(
            "Mgmt guide YoY (mid)",
            f"{guide['implied_yoy_mid']:.1%}",
            help=guide.get("source_url"),
        )
    else:
        stub_cols[3].metric("Mgmt guide YoY", "n/a")
    st.caption(intra.get("framing", ""))

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Signal trends (YoY downloads)")
    chart_cols = [
        c
        for c in [
            "browser_rum_downloads_yoy",
            "dd_trace_downloads_yoy",
            "aws_revenue_yoy",
        ]
        if c in df.columns
    ]
    st.line_chart(chart_df.set_index("quarter")[chart_cols])
    st.caption(
        "Year-over-year npm downloads and AWS segment revenue (SEC XBRL). "
        "AWS is a cloud-regime control, not Datadog account usage. "
        "Incomplete npm quarters (coverage < 85%) are excluded from YoY."
    )
with right:
    st.subheader("Reported revenue growth vs walk-forward estimate")
    rev = chart_df.set_index("quarter")[["revenue_yoy"]].rename(
        columns={"revenue_yoy": "reported YoY"}
    )
    if not preds.empty:
        overlay = preds.set_index("quarter")[["pred", "naive_persistence"]].rename(
            columns={
                "pred": "ridge (lag-1 signals)",
                "naive_persistence": "naive persistence",
            }
        )
        rev = rev.join(overlay, how="left")
    st.line_chart(rev)
    st.caption(
        "Reported growth is SEC-based. The ridge model uses prior-quarter "
        "npm YoY only (no same-quarter leakage)."
    )

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Lead–lag (signal YoY vs revenue YoY)")
    pretty = ll.copy()
    pretty["corr"] = pretty["corr"].map(lambda x: None if pd.isna(x) else round(x, 3))
    st.dataframe(pretty, width="stretch", hide_index=True)
    st.caption(
        "Lag k is a calendar-quarter lag (not a row shift). "
        "Lagged signals may come from before the model-start quarter."
    )
with c2:
    st.subheader("How the call is formed")
    if estimate:
        st.write(
            f"**{estimate.get('quarter')}** ridge estimate "
            f"**{estimate['pred']:.1%}** vs persistence baseline "
            f"**{estimate['naive_persistence']:.1%}**."
        )
        st.write(
            "**Tracking ahead** means the lag-1 npm composite maps to a "
            "growth estimate at least 1pp above the last reported growth rate. "
            "**Behind** is the symmetric case. This is a business-activity "
            "read, not a buy/sell recommendation."
        )
        contrib = estimate.get("contributions") or {}
        if contrib:
            st.write("Standardized feature contributions to the estimate:")
            st.json({k: round(v, 4) for k, v in contrib.items()})
    else:
        st.warning("Not enough complete quarters to form an estimate.")
with c3:
    st.subheader("Out-of-sample validation")
    ridge = walk.get("ridge", walk)
    naive = walk.get("naive_persistence", {})
    st.write(
        "Ridge, all expanding-window forecasts"
        if ridge
        else "No walk-forward results"
    )
    if ridge:
        st.json(
            {
                "n_test": ridge.get("n_test"),
                "RMSE": round(ridge.get("rmse", 0), 4),
                "MAPE": round(ridge.get("mape", 0), 4),
                "directional_hit_rate": round(
                    ridge.get("directional_hit_rate", 0), 3
                ),
                "directional_change_hit_rate": round(
                    ridge.get("directional_change_hit_rate", 0), 3
                )
                if ridge.get("directional_change_hit_rate") is not None
                else None,
            }
        )
    rum_only = walk.get("ridge_rum_lag1_only") or {}
    npm_aws = walk.get("ridge_npm_aws_lag1") or {}
    if rum_only:
        st.write("Ridge, RUM lag-1 only (all OOS)")
        st.json(
            {
                "RMSE": round(rum_only.get("rmse", 0), 4),
                "MAPE": round(rum_only.get("mape", 0), 4),
            }
        )
    if npm_aws:
        st.write("Ridge, npm + AWS lag-1 control (all OOS)")
        st.json(
            {
                "RMSE": round(npm_aws.get("rmse", 0), 4),
                "MAPE": round(npm_aws.get("mape", 0), 4),
                "directional_change_hit_rate": round(
                    npm_aws.get("directional_change_hit_rate", 0), 3
                ),
            }
        )
    if naive:
        st.write("Naive persistence baseline (all OOS)")
        st.json(
            {
                "RMSE": round(naive.get("rmse", 0), 4),
                "MAPE": round(naive.get("mape", 0), 4),
                "directional_hit_rate": round(
                    naive.get("directional_hit_rate", 0), 3
                ),
            }
        )
    recent = walk.get("ridge_recent_window") or {}
    recent_naive = walk.get("naive_persistence_recent_window") or {}
    if recent:
        quarters = ", ".join(walk.get("recent_window_quarters") or [])
        st.write(f"Recent window ({quarters or 'last 4'})")
        st.json(
            {
                "ridge_RMSE": round(recent.get("rmse", 0), 4),
                "persistence_RMSE": round(recent_naive.get("rmse", 0), 4),
                "ridge_change_hit": round(
                    recent.get("directional_change_hit_rate", 0), 3
                ),
            }
        )

st.divider()
st.subheader("Evidence, freshness, and limitations")
st.markdown(
    f"""
- SEC target: {summary.get("sources", {}).get("sec")}
- npm source: {summary.get("sources", {}).get("npm")}
- Cloud segments: {summary.get("sources", {}).get("sec_xbrl")} (AWS, Google Cloud, MSFT Intelligent Cloud XBRL)
- Attention: {summary.get("sources", {}).get("wikimedia")} (Datadog + New Relic placebo). Google Trends was not scraped.
- Hiring is **not** ingested (licensed job boards only).
- Datadog 10-K: https://www.sec.gov/Archives/edgar/data/1561550/000162828026008819/ddog-20251231.htm
- Raw files under `data/`. Q4 flags: `q4_derived_from_fy`.
- {summary.get("caveat")}
"""
)
if "qc_flags" in df.columns:
    flagged = df[df["qc_flags"].fillna("").astype(str).str.len() > 0][
        ["quarter", "qc_flags"]
    ]
    if not flagged.empty:
        st.caption("Quality flags")
        st.dataframe(flagged, width="stretch", hide_index=True)
