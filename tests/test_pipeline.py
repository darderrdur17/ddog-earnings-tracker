from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from ddog_tracker.collectors.npm_downloads import daterange_chunks
from ddog_tracker.collectors.sec_revenue import revenue_from_company_facts
from ddog_tracker.config import Settings
from ddog_tracker.features import (
    aggregate_npm_quarterly,
    build_panel,
    expected_days_in_quarter,
    lead_lag_table,
    period_matched_yoy,
    shift_by_calendar_quarters,
    shift_quarter,
    stub_window,
    stub_yoy_from_daily,
)
from ddog_tracker.http_client import HttpError, JsonHttpClient
from ddog_tracker.model import next_quarter, walk_forward


FIXTURES = Path(__file__).parent / "fixtures"


def test_q4_is_fy_minus_q1_q3():
    payload = json.loads((FIXTURES / "sec_company_facts.json").read_text())
    out = revenue_from_company_facts(payload)
    q4 = out.set_index("quarter").loc["2022Q4"]
    assert q4["source"] == "fy_residual"
    assert q4["revenue"] == pytest.approx(400.0)


def test_period_matched_yoy_not_row_shift():
    quarters = pd.Series(["2022Q1", "2022Q2", "2022Q3", "2022Q4", "2023Q2"])
    values = pd.Series([100.0, 110.0, 120.0, 130.0, 121.0])
    yoy = period_matched_yoy(values, quarters)
    assert pd.isna(yoy.iloc[0])
    assert yoy.iloc[4] == pytest.approx(0.1)
    # A naive 4-row shift would compare 2023Q2 to 2022Q1 (21%), not 2022Q2.


def test_signals_complete_false_when_npm_missing():
    from ddog_tracker.features import build_panel

    revenue = pd.DataFrame(
        {
            "quarter": ["2022Q1"],
            "end": [pd.Timestamp("2022-03-31")],
            "revenue": [1.0],
            "source": ["sec_frame"],
        }
    )
    npm = pd.DataFrame(
        {
            "quarter": ["2022Q2"],
            "browser_rum_downloads": [10],
            "browser_rum_downloads_n_days": [90],
            "browser_rum_downloads_coverage": [1.0],
            "browser_rum_downloads_complete": [True],
            "browser_rum_downloads_yoy": [0.1],
        }
    )
    panel = build_panel(revenue, [npm])
    assert bool(panel.loc[0, "signals_complete"]) is False


def test_incomplete_quarter_blocks_yoy():
    daily = pd.DataFrame(
        {
            "quarter": ["2022Q1"] * 90 + ["2023Q1"] * 10,
            "browser_rum_downloads": [1] * 100,
        }
    )
    q = aggregate_npm_quarterly(daily, "browser_rum_downloads", 0.85)
    row_2023 = q.set_index("quarter").loc["2023Q1"]
    assert not bool(row_2023["browser_rum_downloads_complete"])
    assert pd.isna(row_2023["browser_rum_downloads_yoy"])


def test_lead_lag_uses_yoy_and_counts_n():
    panel = pd.DataFrame(
        {
            "quarter": ["2023Q1", "2023Q2", "2023Q3", "2023Q4", "2024Q1"],
            "revenue_yoy": [0.2, 0.21, 0.22, 0.23, 0.24],
            "sig_yoy": [0.1, 0.12, 0.11, 0.15, 0.16],
        }
    )
    table = lead_lag_table(panel, ["sig_yoy"], max_lag=1)
    lag0 = table.set_index("lag_quarters").loc[0]
    assert lag0["n"] == 5
    assert lag0["corr"] > 0.9


def test_calendar_lag_does_not_use_row_shift_across_gaps():
    quarters = pd.Series(["2022Q3", "2022Q4", "2023Q2"])
    values = pd.Series([1.0, 2.0, 3.0])
    lagged = shift_by_calendar_quarters(values, quarters, 1)
    # 2023Q2 lag-1 is 2023Q1 (missing), not 2022Q4 from the prior row.
    assert pd.isna(lagged.iloc[2])
    assert lagged.iloc[1] == 1.0
    assert shift_quarter("2023Q1", 1) == "2022Q4"


def test_lead_lag_keeps_pre_window_lagged_signals():
    panel = pd.DataFrame(
        {
            "quarter": ["2022Q4", "2023Q1", "2023Q2"],
            "revenue_yoy": [0.4, 0.3, 0.25],
            "sig_yoy": [1.2, 0.7, 0.5],
        }
    )
    table = lead_lag_table(
        panel, ["sig_yoy"], max_lag=1, start_quarter="2023Q1"
    )
    lag1 = table.set_index("lag_quarters").loc[1]
    assert lag1["n"] == 2  # 2023Q1 uses 2022Q4; 2023Q2 uses 2023Q1


def test_qc_flags_numpy_bool_incomplete():
    from ddog_tracker.features import build_panel

    revenue = pd.DataFrame(
        {
            "quarter": ["2023Q1"],
            "end": [pd.Timestamp("2023-03-31")],
            "revenue": [1.0],
            "source": ["sec_frame"],
        }
    )
    npm = pd.DataFrame(
        {
            "quarter": ["2023Q1"],
            "browser_rum_downloads": [10],
            "browser_rum_downloads_n_days": [10],
            "browser_rum_downloads_coverage": [0.1],
            "browser_rum_downloads_complete": [False],
            "browser_rum_downloads_yoy": [pd.NA],
        }
    )
    panel = build_panel(revenue, [npm])
    flags = str(panel.loc[0, "qc_flags"])
    assert "incomplete:browser_rum_downloads" in flags
    assert "incomplete:signals" not in flags


def test_walk_forward_never_trains_on_future_rows():
    rows = []
    for i in range(10):
        rows.append(
            {
                "quarter": f"202{i // 4}Q{(i % 4) + 1}",
                "revenue_yoy": 0.2 + i * 0.01,
                "f1": 0.1 + i * 0.01,
            }
        )
    panel = pd.DataFrame(rows)
    settings = Settings(root=Path("."), min_train_rows=6, test_horizon=4)
    preds, metrics = walk_forward(panel, ["f1"], settings)
    assert len(preds) == 4
    assert metrics["ridge"]["n_test"] == 4
    assert metrics["ridge_recent_window"]["n_test"] == 4
    assert "directional_change_hit_rate" in metrics["ridge"]
    assert list(preds["quarter"]) == list(panel["quarter"].iloc[6:])


def test_next_quarter_wraps_year():
    assert next_quarter("2025Q4") == "2026Q1"
    assert next_quarter("2026Q2") == "2026Q3"


def test_expected_days_q1_non_leap():
    assert expected_days_in_quarter("2023Q1") == 90


def test_daterange_chunks_cover_end_inclusive():
    from datetime import date

    chunks = daterange_chunks(date(2022, 1, 1), date(2022, 1, 10), 7)
    assert chunks[0] == (date(2022, 1, 1), date(2022, 1, 7))
    assert chunks[-1][1] == date(2022, 1, 10)


def test_http_retries_then_succeeds(tmp_path):
    settings = Settings(root=tmp_path, http_retries=3, cache_ttl_seconds=60)
    client = JsonHttpClient(settings)

    class Boom:
        def __init__(self):
            self.n = 0

        def get(self, *args, **kwargs):
            self.n += 1
            if self.n < 3:
                raise ConnectionError("down")

            class Resp:
                status_code = 200

                def raise_for_status(self):
                    return None

                def json(self):
                    return {"ok": True}

            return Resp()

    client.session = Boom()
    with patch("ddog_tracker.http_client.time.sleep"):
        assert client.get_json("https://example.test/x", cache=False) == {"ok": True}
    assert client.session.n == 3


def test_sec_missing_tag_raises():
    from ddog_tracker.collectors.sec_revenue import revenue_from_company_facts

    with pytest.raises(RuntimeError, match="missing revenue tags"):
        revenue_from_company_facts({"facts": {"us-gaap": {}}})


def test_xbrl_quarter_not_ytd():
    from ddog_tracker.collectors.sec_segment import (
        calendar_quarter_from_end,
        parse_segment_revenue,
        period_kind,
        segment_quarters_from_rows,
    )
    from datetime import date

    assert period_kind(date(2026, 4, 1), date(2026, 6, 30)) == "quarter"
    assert period_kind(date(2026, 1, 1), date(2026, 6, 30)) == "other"
    assert period_kind(date(2026, 1, 1), date(2026, 12, 31)) == "annual"
    assert calendar_quarter_from_end(date(2026, 6, 30)) == "2026Q2"

    xml = """<?xml version="1.0"?>
    <xbrl xmlns="http://www.xbrl.org/2003/instance"
          xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
          xmlns:us-gaap="http://fasb.org/us-gaap/2024">
      <context id="q">
        <entity>
          <identifier scheme="http://www.sec.gov/CIK">0001018724</identifier>
          <segment>
            <xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">amzn:AmazonWebServicesSegmentMember</xbrldi:explicitMember>
          </segment>
        </entity>
        <period><startDate>2026-04-01</startDate><endDate>2026-06-30</endDate></period>
      </context>
      <context id="ytd">
        <entity>
          <identifier scheme="http://www.sec.gov/CIK">0001018724</identifier>
          <segment>
            <xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">amzn:AmazonWebServicesSegmentMember</xbrldi:explicitMember>
          </segment>
        </entity>
        <period><startDate>2026-01-01</startDate><endDate>2026-06-30</endDate></period>
      </context>
      <us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax contextRef="q" unitRef="usd">100</us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax>
      <us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax contextRef="ytd" unitRef="usd">250</us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax>
    </xbrl>
    """
    rows = parse_segment_revenue(xml, "AmazonWebServicesSegmentMember")
    kinds = {r["kind"] for r in rows}
    assert "quarter" in kinds
    assert "other" in kinds
    q = segment_quarters_from_rows(rows, calendar_fy=True)
    assert list(q["quarter"]) == ["2026Q2"]
    assert float(q["aws_revenue"].iloc[0]) == 100.0 if "aws_revenue" in q.columns else float(q["revenue"].iloc[0]) == 100.0


def test_wiki_monthly_needs_three_months():
    from ddog_tracker.features import aggregate_monthly_quarterly

    monthly = pd.DataFrame(
        {
            "quarter": ["2023Q1", "2023Q1", "2023Q2", "2023Q2", "2023Q2", "2024Q1", "2024Q1", "2024Q1"],
            "wiki_datadog_views": [10, 10, 5, 5, 5, 22, 22, 22],
        }
    )
    q = aggregate_monthly_quarterly(monthly, "wiki_datadog_views", 1.0)
    by = q.set_index("quarter")
    assert not bool(by.loc["2023Q1", "wiki_datadog_views_complete"])
    assert pd.isna(by.loc["2024Q1", "wiki_datadog_views_yoy"])
    complete = monthly.copy()
    complete.loc[len(complete)] = {"quarter": "2023Q1", "wiki_datadog_views": 10}
    q2 = aggregate_monthly_quarterly(complete, "wiki_datadog_views", 1.0)
    by2 = q2.set_index("quarter")
    assert bool(by2.loc["2023Q1", "wiki_datadog_views_complete"])
    assert by2.loc["2024Q1", "wiki_datadog_views_yoy"] == pytest.approx(1.2)


def test_wiki_incomplete_does_not_fail_npm_complete():
    revenue = pd.DataFrame(
        {
            "quarter": ["2023Q1"],
            "end": [pd.Timestamp("2023-03-31")],
            "revenue": [1.0],
            "source": ["sec_frame"],
        }
    )
    npm = pd.DataFrame(
        {
            "quarter": ["2023Q1"],
            "browser_rum_downloads": [10],
            "browser_rum_downloads_n_days": [90],
            "browser_rum_downloads_coverage": [1.0],
            "browser_rum_downloads_complete": [True],
            "browser_rum_downloads_yoy": [0.1],
        }
    )
    wiki = pd.DataFrame(
        {
            "quarter": ["2023Q1"],
            "wiki_datadog_views": [1],
            "wiki_datadog_views_n_months": [1],
            "wiki_datadog_views_coverage": [0.33],
            "wiki_datadog_views_complete": [False],
            "wiki_datadog_views_yoy": [pd.NA],
        }
    )
    panel = build_panel(
        revenue, [npm, wiki], required_complete_cols=["browser_rum_downloads_complete"]
    )
    assert bool(panel.loc[0, "signals_complete"]) is True


def test_http_gives_up(tmp_path):
    settings = Settings(root=tmp_path, http_retries=2)
    client = JsonHttpClient(settings)

    class AlwaysFail:
        def get(self, *args, **kwargs):
            raise ConnectionError("down")

    client.session = AlwaysFail()
    with patch("ddog_tracker.http_client.time.sleep"):
        with pytest.raises(HttpError):
            client.get_json("https://example.test/x", cache=False)


def test_stub_window_same_day_of_quarter():
    from datetime import date

    start, end = stub_window("2026Q3", date(2026, 9, 2))
    assert start == date(2026, 7, 1)
    assert end == date(2026, 9, 2)
    prior_start, prior_end = stub_window("2025Q3", date(2026, 9, 2))
    assert prior_start == date(2025, 7, 1)
    assert prior_end == date(2025, 9, 2)
    q2_start, q2_end = stub_window("2024Q2", date(2026, 9, 2))
    assert q2_start == date(2024, 4, 1)
    assert q2_end == date(2024, 6, 3)


def test_stub_yoy_fixed_dates_no_network():
    from datetime import date

    days = pd.date_range("2025-07-01", "2026-09-02", freq="D")
    daily = pd.DataFrame(
        {
            "date": days,
            "browser_rum_downloads": [
                2 if d >= pd.Timestamp("2026-07-01") else 1 for d in days
            ],
        }
    )
    out = stub_yoy_from_daily(
        daily, "browser_rum_downloads", "2026Q3", date(2026, 9, 2)
    )
    assert out["window_start"] == "2026-07-01"
    assert out["window_end"] == "2026-09-02"
    assert out["prior_window_start"] == "2025-07-01"
    assert out["prior_window_end"] == "2025-09-02"
    assert out["elapsed_days"] == 64
    assert out["quarter_days"] == 92
    assert out["coverage"] == pytest.approx(64 / 92)
    assert out["yoy"] == pytest.approx(1.0)


def test_last_complete_npm_date_drops_trailing_zeros():
    from datetime import date

    rum = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-31", "2026-09-01", "2026-09-02", "2026-09-03"]),
            "browser_rum_downloads": [100, 90, 0, 0],
        }
    )
    trace = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-31", "2026-09-01", "2026-09-02", "2026-09-03"]),
            "dd_trace_downloads": [80, 70, 0, 0],
        }
    )
    from ddog_tracker.features import last_complete_npm_date

    assert last_complete_npm_date(
        {
            "browser_rum_downloads": rum,
            "dd_trace_downloads": trace,
        },
        fallback=date(2026, 9, 3),
    ) == date(2026, 9, 1)


def test_stub_window_caps_at_quarter_end():
    from datetime import date

    # as_of is late in Q4; mapping onto Q1 should cap at 31 Mar.
    start, end = stub_window("2023Q1", date(2023, 12, 31))
    assert start == date(2023, 1, 1)
    assert end == date(2023, 3, 31)
    assert expected_days_in_quarter("2023Q1") == 90
