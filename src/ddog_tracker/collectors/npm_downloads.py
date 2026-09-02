from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from ..config import Settings
from ..http_client import JsonHttpClient


def daterange_chunks(start: date, end: date, chunk_days: int) -> list[tuple[date, date]]:
    if end < start:
        raise ValueError("end must be on or after start")
    chunks: list[tuple[date, date]] = []
    cursor = start
    delta = timedelta(days=chunk_days - 1)
    while cursor <= end:
        chunk_end = min(cursor + delta, end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return chunks


def fetch_npm_package(
    client: JsonHttpClient,
    settings: Settings,
    package: str,
    label: str,
    end: date | None = None,
) -> pd.DataFrame:
    end = end or date.today()
    rows: list[dict[str, object]] = []
    for start, stop in daterange_chunks(settings.npm_start, end, settings.npm_chunk_days):
        url = (
            "https://api.npmjs.org/downloads/range/"
            f"{start.isoformat()}:{stop.isoformat()}/{package}"
        )
        payload = client.get_json(url)
        downloads = payload.get("downloads") if isinstance(payload, dict) else None
        if not downloads:
            raise RuntimeError(
                f"npm range {start.isoformat()}:{stop.isoformat()} "
                f"returned no downloads for {package}"
            )
        rows.extend(downloads)
    if not rows:
        raise RuntimeError(f"No npm downloads returned for {package}")
    daily = pd.DataFrame(rows).drop_duplicates("day")
    daily["date"] = pd.to_datetime(daily["day"])
    daily = daily.sort_values("date")
    daily["quarter"] = daily["date"].dt.to_period("Q").astype(str)
    daily["package"] = package
    daily = daily.rename(columns={"downloads": label})
    return daily[["date", "day", "quarter", "package", label]]
