from __future__ import annotations

import re
from typing import Any

import pandas as pd

from ..config import Settings
from ..http_client import JsonHttpClient

REVENUE_TAGS = (
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
)
QUARTER_FRAME = re.compile(r"^CY(\d{4})Q([1-4])$")
ANNUAL_FRAME = re.compile(r"^CY(\d{4})$")


def fetch_sec_revenue(client: JsonHttpClient, settings: Settings) -> pd.DataFrame:
    payload = client.get_json(settings.sec_url)
    return revenue_from_company_facts(payload)


def revenue_from_company_facts(payload: dict[str, Any]) -> pd.DataFrame:
    """Build a quarterly revenue series, deriving Q4 from annual minus Q1–Q3.

    SEC Company Facts for DDOG expose CY*Q1–Q3 frames plus CY* annual totals,
    but not CY*Q4. Using a 4-row shift for YoY is therefore invalid until Q4
    is reconstructed.
    """
    try:
        facts = payload["facts"]["us-gaap"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("SEC Company Facts payload missing us-gaap facts") from exc
    try:
        tag = next(name for name in REVENUE_TAGS if name in facts)
    except StopIteration as exc:
        raise RuntimeError(
            f"SEC facts missing revenue tags {REVENUE_TAGS}"
        ) from exc
    units = facts[tag]["units"]["USD"]

    quarterly_rows: list[dict[str, Any]] = []
    annual_rows: list[dict[str, Any]] = []
    for item in units:
        frame = item.get("frame") or ""
        form = item.get("form")
        if form not in {"10-Q", "10-K"} or item.get("val") is None:
            continue
        q_match = QUARTER_FRAME.match(frame)
        a_match = ANNUAL_FRAME.match(frame)
        if q_match:
            year, qtr = int(q_match.group(1)), int(q_match.group(2))
            quarterly_rows.append(
                {
                    "year": year,
                    "qtr": qtr,
                    "quarter": f"{year}Q{qtr}",
                    "end": item.get("end"),
                    "start": item.get("start"),
                    "revenue": float(item["val"]),
                    "frame": frame,
                    "form": form,
                    "source": "sec_frame",
                }
            )
        elif a_match:
            annual_rows.append(
                {
                    "year": int(a_match.group(1)),
                    "revenue": float(item["val"]),
                    "frame": frame,
                    "form": form,
                }
            )

    quarterly = (
        pd.DataFrame(quarterly_rows)
        .sort_values(["quarter", "form"])
        .drop_duplicates("quarter", keep="last")
    )
    annual = (
        pd.DataFrame(annual_rows)
        .sort_values(["year", "form"])
        .drop_duplicates("year", keep="last")
        if annual_rows
        else pd.DataFrame(columns=["year", "revenue", "frame", "form"])
    )

    derived = []
    for _, fy in annual.iterrows():
        year = int(fy["year"])
        parts = quarterly[quarterly["year"] == year]
        have = set(parts["qtr"].tolist())
        if 4 in have or not {1, 2, 3}.issubset(have):
            continue
        q4_rev = float(fy["revenue"]) - float(parts["revenue"].sum())
        if q4_rev <= 0:
            continue
        derived.append(
            {
                "year": year,
                "qtr": 4,
                "quarter": f"{year}Q4",
                "end": f"{year}-12-31",
                "start": f"{year}-10-01",
                "revenue": q4_rev,
                "frame": f"CY{year}Q4",
                "form": "10-K",
                "source": "fy_residual",
            }
        )

    out = pd.concat([quarterly, pd.DataFrame(derived)], ignore_index=True)
    out["end"] = pd.to_datetime(out["end"])
    out["start"] = pd.to_datetime(out["start"])
    return out.sort_values("end").reset_index(drop=True)
