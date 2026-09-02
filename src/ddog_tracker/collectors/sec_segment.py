from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from xml.etree import ElementTree as ET

import pandas as pd

from ..config import Settings
from ..http_client import HttpError, JsonHttpClient

REVENUE_TAGS = {
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
}


@dataclass(frozen=True)
class SegmentSpec:
    cik: str
    label: str
    member: str
    display: str
    calendar_fy: bool


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _parse_date(text: str | None) -> date | None:
    if not text:
        return None
    return datetime.strptime(text[:10], "%Y-%m-%d").date()


def calendar_quarter_from_end(end: date) -> str:
    return f"{end.year}Q{(end.month - 1) // 3 + 1}"


def period_kind(start: date, end: date) -> str:
    days = (end - start).days + 1
    if 80 <= days <= 102:
        return "quarter"
    if 350 <= days <= 380:
        return "annual"
    return "other"


def xbrl_candidates(primary_document: str) -> list[str]:
    if not primary_document.lower().endswith(".htm"):
        return [primary_document]
    stem = primary_document[:-4]
    return [f"{stem}_htm.xml", f"{stem}.xml"]


def parse_segment_revenue(xml_text: str, member: str) -> list[dict[str, Any]]:
    """Extract duration revenue facts for a business-segment member."""
    root = ET.fromstring(xml_text)
    contexts: dict[str, dict[str, Any]] = {}
    for ctx in root.findall("{http://www.xbrl.org/2003/instance}context"):
        cid = ctx.get("id")
        if not cid:
            continue
        members = [
            (em.text or "")
            for em in ctx.findall(".//{http://xbrl.org/2006/xbrldi}explicitMember")
        ]
        if not any(member in m for m in members):
            continue
        start = _parse_date(
            ctx.findtext(".//{http://www.xbrl.org/2003/instance}startDate")
        )
        end = _parse_date(
            ctx.findtext(".//{http://www.xbrl.org/2003/instance}endDate")
        )
        if start is None or end is None:
            continue
        contexts[cid] = {
            "start": start,
            "end": end,
            "kind": period_kind(start, end),
        }

    rows: list[dict[str, Any]] = []
    for el in root.iter():
        cref = el.attrib.get("contextRef")
        if cref not in contexts or not el.text:
            continue
        if _local(el.tag) not in REVENUE_TAGS:
            continue
        try:
            value = float(el.text.replace(",", ""))
        except ValueError:
            continue
        meta = contexts[cref]
        rows.append(
            {
                "start": meta["start"],
                "end": meta["end"],
                "kind": meta["kind"],
                "revenue": value,
                "quarter": calendar_quarter_from_end(meta["end"]),
            }
        )
    return rows


def _filing_xml_urls(cik: str, accession: str, primary_document: str) -> list[str]:
    acc = accession.replace("-", "")
    cik_num = str(int(cik))
    base = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc}"
    return [f"{base}/{name}" for name in xbrl_candidates(primary_document)]


def fetch_issuer_filings(
    client: JsonHttpClient, cik: str, filed_from: str
) -> list[dict[str, str]]:
    padded = cik.zfill(10)
    payload = client.get_json(
        f"https://data.sec.gov/submissions/CIK{padded}.json"
    )
    recent = payload["filings"]["recent"]
    out: list[dict[str, str]] = []
    for form, acc, doc, report, filed in zip(
        recent["form"],
        recent["accessionNumber"],
        recent["primaryDocument"],
        recent["reportDate"],
        recent["filingDate"],
    ):
        if form not in {"10-Q", "10-K"}:
            continue
        if (report or filed) < filed_from:
            continue
        out.append(
            {
                "form": form,
                "accession": acc,
                "document": doc,
                "report_date": report,
                "filed": filed,
            }
        )
    return out


def _download_xbrl(client: JsonHttpClient, cik: str, filing: dict[str, str]) -> str | None:
    last_error: Exception | None = None
    for url in _filing_xml_urls(cik, filing["accession"], filing["document"]):
        try:
            return client.get_text(url)
        except HttpError as exc:
            last_error = exc
            if "404" not in str(exc):
                raise
    if last_error:
        return None
    return None


def segment_quarters_from_rows(
    rows: list[dict[str, Any]], calendar_fy: bool
) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["quarter", "end", "revenue", "source"])
    frame = pd.DataFrame(rows)
    quarterly = frame[frame["kind"] == "quarter"].copy()
    quarterly = (
        quarterly.sort_values(["quarter", "end"])
        .drop_duplicates("quarter", keep="last")
    )
    if calendar_fy:
        annual = (
            frame[frame["kind"] == "annual"]
            .sort_values("end")
            .drop_duplicates("quarter", keep="last")
        )
        derived = []
        for _, fy in annual.iterrows():
            year = fy["end"].year
            parts = quarterly[quarterly["quarter"].str.startswith(str(year))]
            have = set(int(q[-1]) for q in parts["quarter"])
            if 4 in have or not {1, 2, 3}.issubset(have):
                continue
            q4_rev = float(fy["revenue"]) - float(parts["revenue"].sum())
            if q4_rev <= 0:
                continue
            derived.append(
                {
                    "quarter": f"{year}Q4",
                    "end": date(year, 12, 31),
                    "revenue": q4_rev,
                    "source": "fy_residual",
                }
            )
        quarterly = pd.concat(
            [
                quarterly.assign(source="sec_xbrl"),
                pd.DataFrame(derived),
            ],
            ignore_index=True,
        )
    else:
        quarterly = quarterly.assign(source="sec_xbrl")
    quarterly["end"] = pd.to_datetime(quarterly["end"])
    return (
        quarterly.sort_values("end")
        .drop_duplicates("quarter", keep="last")
        .reset_index(drop=True)[["quarter", "end", "revenue", "source"]]
    )


def fetch_cloud_segment(
    client: JsonHttpClient, settings: Settings, spec: SegmentSpec
) -> pd.DataFrame:
    filings = fetch_issuer_filings(client, spec.cik, settings.sec_filings_from)
    rows: list[dict[str, Any]] = []
    for filing in filings:
        xml_text = _download_xbrl(client, spec.cik, filing)
        time.sleep(0.15)
        if not xml_text:
            continue
        parsed = parse_segment_revenue(xml_text, spec.member)
        for row in parsed:
            row["form"] = filing["form"]
            row["accession"] = filing["accession"]
        rows.extend(parsed)
    out = segment_quarters_from_rows(rows, spec.calendar_fy)
    if out.empty:
        raise RuntimeError(f"No quarterly {spec.display} segment revenue parsed")
    return out.rename(columns={"revenue": spec.label, "source": f"{spec.label}_source"})


def fetch_all_cloud_segments(
    client: JsonHttpClient, settings: Settings
) -> list[pd.DataFrame]:
    frames = []
    for cik, label, member, display, calendar_fy in settings.cloud_segments:
        spec = SegmentSpec(cik, label, member, display, calendar_fy)
        frames.append(fetch_cloud_segment(client, settings, spec))
    return frames
