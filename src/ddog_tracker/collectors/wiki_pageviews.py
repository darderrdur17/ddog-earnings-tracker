from __future__ import annotations

from datetime import date

import pandas as pd

from ..config import Settings
from ..http_client import JsonHttpClient


def wiki_pageviews_url(article: str, start: str, end: str) -> str:
    return (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{article}/monthly/{start}/{end}"
    )


def monthly_to_daily_like(payload: dict, label: str) -> pd.DataFrame:
    items = payload.get("items") if isinstance(payload, dict) else None
    if not items:
        raise RuntimeError(f"Wikimedia pageviews returned no items for {label}")
    rows = []
    for item in items:
        ts = str(item.get("timestamp", ""))
        if len(ts) < 6:
            continue
        year, month = int(ts[:4]), int(ts[4:6])
        rows.append(
            {
                "date": pd.Timestamp(year=year, month=month, day=1),
                "quarter": f"{year}Q{(month - 1) // 3 + 1}",
                label: int(item["views"]),
            }
        )
    if not rows:
        raise RuntimeError(f"Could not parse Wikimedia timestamps for {label}")
    return pd.DataFrame(rows).sort_values("date")


def fetch_wiki_article(
    client: JsonHttpClient,
    settings: Settings,
    article: str,
    label: str,
    end: date | None = None,
) -> pd.DataFrame:
    end = end or date.today()
    end_ts = f"{end.year:04d}{end.month:02d}0100"
    url = wiki_pageviews_url(article, settings.wiki_start, end_ts)
    payload = client.get_json(url)
    return monthly_to_daily_like(payload, label)
