from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root: Path
    user_agent: str = (
        "DDOG-research-prototype/1.0 "
        "(public-data; contact research@example.com)"
    )
    sec_cik: str = "0001561550"
    npm_packages: tuple[tuple[str, str], ...] = (
        ("@datadog/browser-rum", "browser_rum_downloads"),
        ("dd-trace", "dd_trace_downloads"),
    )
    cloud_segments: tuple[tuple[str, str, str, str, bool], ...] = (
        # cik, label, XBRL member fragment, display, calendar fiscal year
        ("0001018724", "aws_revenue", "AmazonWebServicesSegmentMember", "AWS", True),
        ("0001652044", "gcp_revenue", "GoogleCloudMember", "Google Cloud", True),
        (
            "0000789019",
            "msft_ic_revenue",
            "IntelligentCloudMember",
            "MSFT Intelligent Cloud",
            False,
        ),
    )
    wiki_articles: tuple[tuple[str, str], ...] = (
        ("Datadog", "wiki_datadog_views"),
        ("New_Relic", "wiki_newrelic_views"),
    )
    wiki_start: str = "2018010100"
    sec_filings_from: str = "2020-01-01"
    npm_start: date = date(2021, 7, 1)
    npm_chunk_days: int = 180
    analysis_start_quarter: str = "2023Q1"
    min_quarter_coverage: float = 0.85
    ridge_alpha: float = 10.0
    min_train_rows: int = 6
    test_horizon: int = 4
    http_timeout: int = 45
    http_retries: int = 5
    cache_ttl_seconds: int = 86_400

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def out_dir(self) -> Path:
        return self.root / "outputs"

    @property
    def sec_url(self) -> str:
        return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{self.sec_cik}.json"


def default_settings(root: Path | None = None) -> Settings:
    if root is None:
        root = Path(__file__).resolve().parents[2]
    return Settings(root=root)
