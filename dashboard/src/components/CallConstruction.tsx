import { LAST_YOY, pct, pp, summary } from "../data";
import { Annotation } from "./Annotation";

const contrib = summary.latest_estimate.contributions;

export function CallConstruction() {
  return (
    <div className="h-full rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <h2 className="text-sm font-medium text-zinc-200">How the {summary.latest_estimate.quarter} call is built</h2>
      <p className="mt-0.5 text-[12px] text-zinc-500">
        Validated lag-1 ridge (not a leading-indicator claim). Signals as of {summary.latest_estimate.signal_as_of_quarter}. Intra-quarter stub is shown separately.
      </p>

      <ol className="mt-4 space-y-3">
        <li className="grid grid-cols-[1.5rem_1fr] gap-2">
          <span className="font-mono text-[11px] text-brass-500">01</span>
          <div>
            <p className="text-[13px] text-zinc-200">Observe prior-quarter npm YoY</p>
            <p className="mt-0.5 font-mono text-[11px] text-zinc-500">
              Features: {summary.feature_cols.join(" · ")}
            </p>
          </div>
        </li>
        <li className="grid grid-cols-[1.5rem_1fr] gap-2">
          <span className="font-mono text-[11px] text-brass-500">02</span>
          <div>
            <p className="text-[13px] text-zinc-200">Standardized contributions</p>
            <div className="mt-2 space-y-2">
              <ContribBar
                name="RUM YoY lag-1"
                value={contrib.browser_rum_downloads_yoy_lag1}
                max={0.03}
              />
              <ContribBar
                name="dd-trace YoY lag-1"
                value={contrib.dd_trace_downloads_yoy_lag1}
                max={0.03}
              />
            </div>
          </div>
        </li>
        <li className="grid grid-cols-[1.5rem_1fr] gap-2">
          <span className="font-mono text-[11px] text-brass-500">03</span>
          <div>
            <p className="text-[13px] text-zinc-200">Compare to persistence, then label</p>
            <div className="mt-2 grid grid-cols-2 gap-2 font-mono text-[12px]">
              <div className="rounded border border-zinc-800 px-2.5 py-2">
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">Ridge</p>
                <p className="mt-1 text-zinc-100">{pct(summary.latest_estimate.pred)}</p>
              </div>
              <div className="rounded border border-zinc-800 px-2.5 py-2">
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">Persistence</p>
                <p className="mt-1 text-zinc-100">{pct(summary.latest_estimate.naive_persistence)}</p>
              </div>
            </div>
          </div>
        </li>
      </ol>

      <div className="mt-4 space-y-2 border-t border-zinc-800/80 pt-3">
        <Annotation
          label={`Ahead / behind vs last reported YoY (${pct(LAST_YOY)}), not vs Street. Threshold is 1pp. Current gap ${pp(summary.latest_estimate.delta_vs_baseline)}.`}
        />
        <Annotation label="AWS is ingested as a lag-1 control (cuts OOS RMSE to 2.6pp) but is not in this call — the call is an instrumentation read, not a restatement of AWS." />
        <Annotation label="This is a business-activity read. It is not a buy or sell signal." />
      </div>
    </div>
  );
}

function ContribBar({ name, value, max }: { name: string; value: number; max: number }) {
  const width = Math.min(100, (Math.abs(value) / max) * 100);
  return (
    <div>
      <div className="flex items-center justify-between font-mono text-[11px] text-zinc-400">
        <span>{name}</span>
        <span>{pp(value, 2)}</span>
      </div>
      <div className="mt-1 h-1 overflow-hidden rounded-full bg-zinc-800">
        <div
          className="h-full rounded-full bg-brass-500/80"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
