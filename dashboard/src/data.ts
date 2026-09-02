import summary from "./analysis_summary.json";

export { summary };

const last = [...summary.chart_panel].reverse().find((row) => row.revenue_yoy != null)!;

export const LAST_REVENUE = last.revenue as number;
export const LAST_REVENUE_M = LAST_REVENUE / 1e6;
export const LAST_YOY = last.revenue_yoy as number;

export const growthSeries = summary.chart_panel.map((row) => {
  const wf = summary.walk_forward_rows.find((w) => w.quarter === row.quarter);
  return {
    quarter: row.quarter,
    reported: row.revenue_yoy == null ? null : row.revenue_yoy * 100,
    ridge: wf ? wf.pred * 100 : null,
    persistence: wf ? wf.naive_persistence * 100 : null,
  };
});

export const signalSeries = summary.chart_panel.map((row) => ({
  quarter: row.quarter,
  rum: row.browser_rum_downloads_yoy == null ? null : row.browser_rum_downloads_yoy * 100,
  trace: row.dd_trace_downloads_yoy == null ? null : row.dd_trace_downloads_yoy * 100,
  aws: row.aws_revenue_yoy == null ? null : row.aws_revenue_yoy * 100,
  wiki: row.wiki_datadog_views_yoy == null ? null : row.wiki_datadog_views_yoy * 100,
  revenue: row.revenue_yoy == null ? null : row.revenue_yoy * 100,
}));

const SIGNAL_LABELS: Record<string, string> = {
  browser_rum_downloads_yoy: "RUM",
  dd_trace_downloads_yoy: "dd-trace",
  aws_revenue_yoy: "AWS",
  gcp_revenue_yoy: "GCP",
  msft_ic_revenue_yoy: "MSFT IC",
  wiki_datadog_views_yoy: "Wiki DDOG",
  wiki_newrelic_views_yoy: "Wiki New Relic",
};

export const leadLag = summary.lead_lag.map((row) => ({
  signal: SIGNAL_LABELS[row.signal] ?? row.signal,
  lag: row.lag_quarters,
  n: row.n,
  corr: row.corr,
}));

export const LEAD_LAG_SIGNALS = ["RUM", "AWS", "Wiki DDOG", "dd-trace"] as const;

export function pct(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`;
}

export function pp(value: number, digits = 1): string {
  const n = value * 100;
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}pp`;
}

export function moneyM(value: number): string {
  return `$${Math.round(value / 1e6).toLocaleString("en-US")}m`;
}
