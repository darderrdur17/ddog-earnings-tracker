from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from .config import Settings
from .features import stub_yoy_from_daily
from .model import next_quarter, walk_forward

# Last public company outlook for the in-progress quarter, from EDGAR 8-K Ex. 99.1.
# Not Street consensus; no vendor scrape.
Q3_2026_GUIDANCE = {
    "quarter": "2026Q3",
    "revenue_low": 1_135_000_000.0,
    "revenue_high": 1_145_000_000.0,
    "as_of": "2026-08-06",
    "filing": "8-K Exhibit 99.1, 6 August 2026",
    "source_url": (
        "https://www.sec.gov/Archives/edgar/data/1561550/"
        "000162828026053829/ex-991x20260630x8k.htm"
    ),
    "note": (
        "Management outlook from the Q2 2026 earnings 8-K. Not a Street "
        "consensus number. No Yahoo/FactSet scrape."
    ),
}


def _corr(a: pd.Series, b: pd.Series) -> tuple[float | None, int]:
    aligned = pd.concat([a, b], axis=1).dropna()
    if len(aligned) < 3:
        return None, int(len(aligned))
    return float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1])), int(len(aligned))


def build_intra_quarter(
    dailies: dict[str, pd.DataFrame],
    modeled: pd.DataFrame,
    estimate: dict[str, Any],
    settings: Settings,
    as_of: date,
    npm_lag: list[str],
) -> dict[str, Any]:
    last_q = str(estimate.get("last_reported_quarter") or modeled["quarter"].iloc[-1])
    in_progress = str(estimate.get("quarter") or next_quarter(last_q))
    rum_col = "browser_rum_downloads"
    trace_col = "dd_trace_downloads"

    rum_now = stub_yoy_from_daily(dailies[rum_col], rum_col, in_progress, as_of)
    trace_now = stub_yoy_from_daily(dailies[trace_col], trace_col, in_progress, as_of)

    last_row = modeled.loc[modeled["quarter"] == last_q].iloc[-1]
    last_rum = last_row.get("browser_rum_downloads_yoy")
    last_trace = last_row.get("dd_trace_downloads_yoy")
    last_rev = float(last_row["revenue_yoy"]) if pd.notna(last_row.get("revenue_yoy")) else None
    ridge = float(estimate["pred"]) if estimate.get("pred") is not None else None

    backtest_rows: list[dict[str, Any]] = []
    stub_panel = modeled.copy()
    rum_stubs: list[float] = []
    trace_stubs: list[float] = []
    for quarter in stub_panel["quarter"].astype(str):
        rum_bt = stub_yoy_from_daily(dailies[rum_col], rum_col, quarter, as_of)
        trace_bt = stub_yoy_from_daily(dailies[trace_col], trace_col, quarter, as_of)
        rum_yoy = rum_bt["yoy"]
        trace_yoy = trace_bt["yoy"]
        rum_stubs.append(float("nan") if rum_yoy is None else float(rum_yoy))
        trace_stubs.append(float("nan") if trace_yoy is None else float(trace_yoy))
        rev = stub_panel.loc[stub_panel["quarter"] == quarter, "revenue_yoy"]
        backtest_rows.append(
            {
                "quarter": quarter,
                "rum_stub_yoy": rum_yoy,
                "dd_trace_stub_yoy": trace_yoy,
                "revenue_yoy": None if rev.empty or pd.isna(rev.iloc[0]) else float(rev.iloc[0]),
            }
        )
    stub_panel["browser_rum_downloads_stub_yoy"] = rum_stubs
    stub_panel["dd_trace_downloads_stub_yoy"] = trace_stubs

    rum_corr, rum_n = _corr(
        stub_panel["browser_rum_downloads_stub_yoy"], stub_panel["revenue_yoy"]
    )
    trace_corr, trace_n = _corr(
        stub_panel["dd_trace_downloads_stub_yoy"], stub_panel["revenue_yoy"]
    )

    stub_features = [
        "browser_rum_downloads_stub_yoy",
        "dd_trace_downloads_stub_yoy",
    ]
    wf_metrics: dict[str, Any] = {}
    beats_persistence = False
    try:
        _, wf_metrics = walk_forward(
            stub_panel, npm_lag + stub_features, settings
        )
        ridge_stub = wf_metrics.get("ridge") or {}
        persist = wf_metrics.get("naive_persistence") or {}
        beats_persistence = (
            ridge_stub.get("rmse") is not None
            and persist.get("rmse") is not None
            and ridge_stub["rmse"] < persist["rmse"]
        )
    except (ValueError, KeyError):
        wf_metrics = {}

    guidance = _guidance_block(modeled, in_progress)

    rum_yoy = rum_now["yoy"]
    note_parts = [
        "Stub is a coincident high-frequency npm update (same-calendar-day window vs a year ago), not a leading indicator.",
        "Lag-1 ridge is the validated model call; the stub is not trained into that call.",
        "Backtest n is small (one stub date per completed quarter).",
    ]
    if rum_corr is not None:
        note_parts.append(
            f"RUM stub YoY vs eventual revenue YoY correlation is {rum_corr:.2f} (n={rum_n}, coincident)."
        )
    if wf_metrics.get("ridge") and wf_metrics.get("naive_persistence"):
        rs = wf_metrics["ridge"]["rmse"]
        ps = wf_metrics["naive_persistence"]["rmse"]
        if rs >= ps:
            note_parts.append(
                f"Walk-forward ridge using lag-1 npm plus same-quarter stub (known as of the stub date) "
                f"RMSE {rs:.3f} does not beat persistence {ps:.3f}."
            )
        else:
            note_parts.append(
                f"Walk-forward ridge with stub RMSE {rs:.3f} beats persistence {ps:.3f}."
            )

    compare = {
        "rum_stub_yoy_vs_last_full_quarter_rum_yoy": (
            None
            if rum_yoy is None or pd.isna(last_rum)
            else float(rum_yoy) - float(last_rum)
        ),
        "ridge_lag1_minus_last_print": (
            None if ridge is None or last_rev is None else ridge - last_rev
        ),
        "rum_stub_minus_ridge_lag1": (
            None if rum_yoy is None or ridge is None else float(rum_yoy) - ridge
        ),
        "interpretation": (
            "Do not treat npm stub YoY as a revenue YoY forecast — scales differ. "
            "Use it as a coincident check on whether package downloads are still "
            "accelerating versus the last completed quarter."
        ),
    }

    return {
        "quarter": in_progress,
        "as_of": as_of.isoformat(),
        "coverage": rum_now["coverage"],
        "elapsed_days": rum_now["elapsed_days"],
        "quarter_days": rum_now["quarter_days"],
        "window_start": rum_now["window_start"],
        "window_end": rum_now["window_end"],
        "prior_window_start": rum_now["prior_window_start"],
        "prior_window_end": rum_now["prior_window_end"],
        "rum_stub_yoy": rum_yoy,
        "dd_trace_stub_yoy": trace_now["yoy"],
        "rum_n_days": rum_now["n_days"],
        "dd_trace_n_days": trace_now["n_days"],
        "last_print_revenue_yoy": last_rev,
        "lag1_ridge_call": ridge,
        "lag1_ridge_quarter": estimate.get("quarter"),
        "last_full_quarter_rum_yoy": None if pd.isna(last_rum) else float(last_rum),
        "last_full_quarter_dd_trace_yoy": (
            None if pd.isna(last_trace) else float(last_trace)
        ),
        "compare": compare,
        "backtest": {
            "method": (
                "Same day-of-quarter offset as as_of, mapped onto each completed "
                "analysis quarter. Coincident vs that quarter's revenue YoY. "
                "Walk-forward adds stub features known as of the stub date to lag-1 npm."
            ),
            "rum_stub_vs_revenue_yoy_corr": rum_corr,
            "rum_stub_n": rum_n,
            "dd_trace_stub_vs_revenue_yoy_corr": trace_corr,
            "dd_trace_stub_n": trace_n,
            "walk_forward_lag1_plus_stub": wf_metrics.get("ridge"),
            "walk_forward_persistence": wf_metrics.get("naive_persistence"),
            "stub_walk_forward_beats_persistence": beats_persistence,
            "rows": backtest_rows,
        },
        "management_guidance": guidance,
        "framing": " ".join(note_parts),
        "label_lag1": "validated lag-1 ridge (no same-quarter npm)",
        "label_stub": "coincident high-frequency stub (sample still small)",
    }


def _guidance_block(modeled: pd.DataFrame, in_progress: str) -> dict[str, Any]:
    raw = dict(Q3_2026_GUIDANCE)
    if in_progress != raw["quarter"]:
        return {
            "available": False,
            "reason": (
                f"Hardcoded EDGAR outlook is for {raw['quarter']}; "
                f"in-progress quarter is {in_progress}."
            ),
        }
    prior_q = f"{int(in_progress[:4]) - 1}{in_progress[4:]}"
    prior = modeled.loc[modeled["quarter"] == prior_q, "revenue"]
    if prior.empty or pd.isna(prior.iloc[0]):
        return {**raw, "available": True, "implied_yoy_mid": None}
    prior_rev = float(prior.iloc[0])
    mid = (raw["revenue_low"] + raw["revenue_high"]) / 2.0
    return {
        **raw,
        "available": True,
        "prior_year_revenue": prior_rev,
        "implied_yoy_low": raw["revenue_low"] / prior_rev - 1.0,
        "implied_yoy_high": raw["revenue_high"] / prior_rev - 1.0,
        "implied_yoy_mid": mid / prior_rev - 1.0,
    }


def sync_dashboard_summary(settings: Settings) -> None:
    src = settings.out_dir / "analysis_summary.json"
    dest_dir = settings.root / "dashboard" / "src"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "analysis_summary.json"
    dest.write_text(src.read_text())
