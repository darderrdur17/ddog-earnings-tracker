import { LAST_YOY, pct, pp, summary } from "../data";
import { Annotation } from "./Annotation";

const intra = summary.intra_quarter;
const guide = intra.management_guidance;

export function StubNowcast() {
  const stubRmse = intra.backtest.walk_forward_lag1_plus_stub?.rmse;
  const persistRmse = intra.backtest.walk_forward_persistence?.rmse;
  const stubVsPersist =
    stubRmse != null && persistRmse != null
      ? intra.backtest.stub_walk_forward_beats_persistence
        ? `beats persistence (${(stubRmse * 100).toFixed(1)}pp vs ${(persistRmse * 100).toFixed(1)}pp RMSE)`
        : `does not beat persistence (${(stubRmse * 100).toFixed(1)}pp vs ${(persistRmse * 100).toFixed(1)}pp RMSE)`
      : "not estimated";

  return (
    <div className="mt-4 rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-zinc-500">
            High-frequency update · coincident, not a lead
          </p>
          <h2 className="mt-1 text-sm font-medium text-zinc-200">
            {intra.quarter} intra-quarter npm stub
          </h2>
          <p className="mt-0.5 text-[12px] text-zinc-500">
            Same-calendar-day window {intra.window_start} → {intra.window_end} vs{" "}
            {intra.prior_window_start} → {intra.prior_window_end}. Coverage{" "}
            {(intra.coverage * 100).toFixed(0)}% of the quarter ({intra.elapsed_days}/
            {intra.quarter_days} days).
          </p>
        </div>
        <div className="w-full max-w-[220px]">
          <div className="flex justify-between font-mono text-[10px] text-zinc-500">
            <span>Quarter elapsed</span>
            <span>
              {intra.elapsed_days}/{intra.quarter_days}
            </span>
          </div>
          <div className="mt-1 h-1 overflow-hidden rounded-full bg-zinc-800">
            <div
              className="h-full bg-brass-500"
              style={{ width: `${Math.min(100, intra.coverage * 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        <CallCard
          kicker="Validated model"
          title="Lag-1 ridge"
          value={pct(intra.lag1_ridge_call)}
          meta={`${intra.lag1_ridge_quarter} revenue YoY call`}
        />
        <CallCard
          kicker="High-frequency update"
          title="RUM stub YoY"
          value={intra.rum_stub_yoy == null ? "n/a" : pct(intra.rum_stub_yoy)}
          meta="npm downloads, not revenue"
        />
        <CallCard
          kicker="Triangulation"
          title="dd-trace stub YoY"
          value={intra.dd_trace_stub_yoy == null ? "n/a" : pct(intra.dd_trace_stub_yoy)}
          meta="Same npm API, second package"
        />
        <CallCard
          kicker="Last print"
          title="Reported YoY"
          value={pct(LAST_YOY)}
          meta={`${summary.latest_estimate.last_reported_quarter} · ${pp(summary.latest_estimate.delta_vs_baseline)} vs ridge`}
        />
      </div>

      {guide.available ? (
        <p className="mt-3 font-mono text-[11px] text-zinc-500">
          Management guidance (EDGAR 8-K Ex. 99.1, {guide.as_of}): revenue $
          {(guide.revenue_low / 1e9).toFixed(3)}–{(guide.revenue_high / 1e9).toFixed(3)}bn
          {guide.implied_yoy_mid != null
            ? ` · implied YoY ${pct(guide.implied_yoy_low)}–${pct(guide.implied_yoy_high)} (mid ${pct(guide.implied_yoy_mid)})`
            : ""}
          . Company outlook, not Street consensus.
        </p>
      ) : (
        <p className="mt-3 font-mono text-[11px] text-zinc-500">
          No Street consensus. Baseline is persistence plus company guidance when disclosed.
        </p>
      )}

      <div className="mt-3 space-y-2 border-t border-zinc-800/80 pt-3">
        <Annotation
          label={`Lag-1 ridge is the validated model. The stub is a coincident high-frequency update; backtest n=${intra.backtest.rum_stub_n}, RUM stub vs revenue YoY corr ${intra.backtest.rum_stub_vs_revenue_yoy_corr?.toFixed(2) ?? "n/a"}. It does not lead earnings.`}
        />
        <Annotation
          label={`Lag-1 npm + same-quarter stub walk-forward ${stubVsPersist}. Persistence remains the RMSE champion unless stated otherwise.`}
        />
      </div>
    </div>
  );
}

function CallCard({
  kicker,
  title,
  value,
  meta,
}: {
  kicker: string;
  title: string;
  value: string;
  meta: string;
}) {
  return (
    <div className="rounded border border-zinc-800 px-3 py-2.5">
      <p className="font-mono text-[10px] uppercase tracking-wider text-zinc-500">{kicker}</p>
      <p className="mt-1 text-[12px] text-zinc-400">{title}</p>
      <p className="mt-1 font-mono text-xl text-zinc-100">{value}</p>
      <p className="mt-1 text-[11px] text-zinc-500">{meta}</p>
    </div>
  );
}
