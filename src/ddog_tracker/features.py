from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

def quarter_start_end(quarter: str) -> tuple[date, date]:
    year, qtr = _parse_quarter(quarter)
    start_month = 1 + (qtr - 1) * 3
    start = date(year, start_month, 1)
    if qtr == 4:
        end = date(year, 12, 31)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)
    return start, end


def expected_days_in_quarter(quarter: str) -> int:
    start, end = quarter_start_end(quarter)
    return (end - start).days + 1


def calendar_quarter_of(day: date) -> str:
    qtr = (day.month - 1) // 3 + 1
    return f"{day.year}Q{qtr}"


def stub_window(quarter: str, as_of: date) -> tuple[date, date]:
    """Inclusive window: quarter start through the same day-of-quarter as as_of.

    The offset is (as_of − start of as_of's calendar quarter), applied to
    `quarter`, then capped at that quarter's last day. No network.
    """
    q_start, q_end = quarter_start_end(quarter)
    ref_start, _ = quarter_start_end(calendar_quarter_of(as_of))
    offset = (as_of - ref_start).days
    stub_end = min(q_start + timedelta(days=offset), q_end)
    if stub_end < q_start:
        stub_end = q_start
    return q_start, stub_end


def sum_daily_window(
    daily: pd.DataFrame, value_col: str, start: date, end: date
) -> tuple[float, int]:
    dates = pd.to_datetime(daily["date"]).dt.date
    mask = (dates >= start) & (dates <= end)
    n_days = int(mask.sum())
    total = float(daily.loc[mask, value_col].sum()) if n_days else 0.0
    return total, n_days


def last_complete_npm_date(
    dailies: dict[str, pd.DataFrame],
    fallback: date | None = None,
) -> date:
    """Latest date where every npm series has a positive download count.

    The npm range API often returns 0 for the current and prior calendar day
    before counts settle. Using those zeros in the intra-quarter stub would
    compare an incomplete current window to a complete prior-year window.
    """
    cap = fallback or date.today()
    last: date | None = None
    for col, daily in dailies.items():
        if col not in daily.columns or daily.empty:
            continue
        positive = daily.loc[daily[col].fillna(0) > 0]
        if positive.empty:
            continue
        series_last = pd.to_datetime(positive["date"]).dt.date.max()
        last = series_last if last is None else min(last, series_last)
    if last is None:
        return cap
    return min(last, cap)


def stub_yoy_from_daily(
    daily: pd.DataFrame,
    value_col: str,
    quarter: str,
    as_of: date,
) -> dict[str, object]:
    start, end = stub_window(quarter, as_of)
    prior_q = f"{int(quarter[:4]) - 1}{quarter[4:]}"
    prior_start, prior_end = stub_window(prior_q, as_of)
    current_sum, n_days = sum_daily_window(daily, value_col, start, end)
    prior_sum, prior_n = sum_daily_window(daily, value_col, prior_start, prior_end)
    expected = expected_days_in_quarter(quarter)
    elapsed = (end - start).days + 1
    yoy: float | None
    if prior_sum in (0, None) or prior_n == 0:
        yoy = None
    else:
        yoy = current_sum / prior_sum - 1.0
    return {
        "quarter": quarter,
        "as_of": as_of.isoformat(),
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "prior_window_start": prior_start.isoformat(),
        "prior_window_end": prior_end.isoformat(),
        "current_sum": current_sum,
        "prior_sum": prior_sum,
        "n_days": n_days,
        "prior_n_days": prior_n,
        "elapsed_days": elapsed,
        "quarter_days": expected,
        "coverage": elapsed / expected if expected else None,
        "yoy": yoy,
    }


def _parse_quarter(quarter: str) -> tuple[int, int]:
    text = str(quarter)
    return int(text[:4]), int(text[-1])


def shift_quarter(quarter: str, lag: int) -> str:
    year, qtr = _parse_quarter(quarter)
    qtr -= lag
    while qtr <= 0:
        qtr += 4
        year -= 1
    while qtr > 4:
        qtr -= 4
        year += 1
    return f"{year}Q{qtr}"


def shift_by_calendar_quarters(
    values: pd.Series, quarters: pd.Series, lag: int
) -> pd.Series:
    """Lag by fiscal quarter, not by row index (safe when quarters are missing)."""
    lookup = dict(zip(quarters.astype(str), values))
    out = []
    for quarter in quarters.astype(str):
        if lag == 0:
            out.append(lookup.get(quarter, np.nan))
            continue
        prior = lookup.get(shift_quarter(quarter, lag))
        out.append(np.nan if prior is None else prior)
    return pd.Series(out, index=getattr(values, "index", None))


def period_matched_yoy(values: pd.Series, quarters: pd.Series) -> pd.Series:
    """YoY using the same fiscal quarter one year earlier, not a row shift."""
    lookup = dict(zip(quarters.astype(str), values))
    out = []
    for quarter, value in zip(quarters.astype(str), values):
        year = int(quarter[:4])
        prior = f"{year - 1}{quarter[4:]}"
        base = lookup.get(prior)
        if base in (None, 0) or pd.isna(base) or pd.isna(value):
            out.append(np.nan)
        else:
            out.append(float(value) / float(base) - 1.0)
    return pd.Series(out, index=getattr(values, "index", None))


def _yoy_if_complete(grouped: pd.DataFrame, label: str) -> pd.Series:
    yoy = period_matched_yoy(grouped[label], grouped["quarter"])
    prior_complete = grouped["quarter"].map(
        lambda q: bool(
            grouped.loc[
                grouped["quarter"] == f"{int(q[:4]) - 1}{q[4:]}",
                "complete",
            ].any()
        )
    )
    return pd.Series(
        np.where(grouped["complete"] & prior_complete, yoy, np.nan),
        index=grouped.index,
    )


def aggregate_npm_quarterly(
    daily: pd.DataFrame,
    label: str,
    min_coverage: float,
) -> pd.DataFrame:
    grouped = daily.groupby("quarter", as_index=False).agg(
        **{label: (label, "sum"), "n_days": (label, "count")}
    )
    grouped["expected_days"] = grouped["quarter"].map(expected_days_in_quarter)
    grouped["coverage"] = grouped["n_days"] / grouped["expected_days"]
    grouped["complete"] = grouped["coverage"] >= min_coverage
    grouped[f"{label}_yoy"] = _yoy_if_complete(grouped, label)
    grouped = grouped.rename(
        columns={
            "coverage": f"{label}_coverage",
            "complete": f"{label}_complete",
            "n_days": f"{label}_n_days",
        }
    )
    return grouped.drop(columns=["expected_days"])


def aggregate_monthly_quarterly(
    monthly: pd.DataFrame,
    label: str,
    min_coverage: float = 1.0,
) -> pd.DataFrame:
    grouped = monthly.groupby("quarter", as_index=False).agg(
        **{label: (label, "sum"), "n_months": (label, "count")}
    )
    grouped["coverage"] = grouped["n_months"] / 3.0
    grouped["complete"] = grouped["coverage"] >= min_coverage
    grouped[f"{label}_yoy"] = _yoy_if_complete(grouped, label)
    return grouped.rename(
        columns={
            "coverage": f"{label}_coverage",
            "complete": f"{label}_complete",
            "n_months": f"{label}_n_months",
        }
    )


def quarterly_yoy_frame(frame: pd.DataFrame, value_col: str) -> pd.DataFrame:
    out = frame.copy()
    out[f"{value_col}_yoy"] = period_matched_yoy(out[value_col], out["quarter"])
    return out


def build_panel(
    revenue: pd.DataFrame,
    extra_quarterlies: list[pd.DataFrame],
    required_complete_cols: list[str] | None = None,
) -> pd.DataFrame:
    panel = revenue.copy()
    panel["revenue_yoy"] = period_matched_yoy(panel["revenue"], panel["quarter"])
    for extra in extra_quarterlies:
        keep = [c for c in extra.columns if c != "end"]
        panel = panel.merge(extra[keep], on="quarter", how="left")
    complete_cols = [
        col for col in panel.columns if col.endswith("_complete")
    ]
    required = required_complete_cols if required_complete_cols is not None else complete_cols
    required = [c for c in required if c in panel.columns]
    if required:
        panel["signals_complete"] = panel[required].eq(True).all(axis=1)
    else:
        panel["signals_complete"] = False
    panel["qc_flags"] = panel.apply(_qc_flags, axis=1)
    return panel.sort_values("end").reset_index(drop=True)


def _qc_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if row.get("source") == "fy_residual":
        flags.append("q4_derived_from_fy")
    for col in row.index:
        if not col.endswith("_complete") or col == "signals_complete":
            continue
        value = row[col]
        if pd.isna(value):
            flags.append(f"missing:{col.replace('_complete', '')}")
        elif value == False:  # noqa: E712 — numpy.bool_ is not `is False`
            flags.append(f"incomplete:{col.replace('_complete', '')}")
    return ",".join(flags)


def lead_lag_table(
    panel: pd.DataFrame,
    signal_yoy_cols: list[str],
    max_lag: int = 4,
    start_quarter: str | None = None,
) -> pd.DataFrame:
    """Correlate signal_{t-k} with revenue_t using calendar lags.

    If start_quarter is set, only revenue quarters on or after that label
    enter the correlation; lagged signals may come from earlier history.
    """
    rows = []
    target_mask = (
        panel["quarter"].astype(str) >= start_quarter
        if start_quarter
        else pd.Series(True, index=panel.index)
    )
    for col in signal_yoy_cols:
        for lag in range(max_lag + 1):
            lagged = shift_by_calendar_quarters(panel[col], panel["quarter"], lag)
            aligned = pd.concat([lagged, panel["revenue_yoy"]], axis=1)
            aligned = aligned.loc[target_mask].dropna()
            if aligned.empty:
                corr = np.nan
            else:
                corr = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
            rows.append(
                {
                    "signal": col,
                    "lag_quarters": lag,
                    "n": int(len(aligned)),
                    "corr": corr,
                }
            )
    return pd.DataFrame(rows)
