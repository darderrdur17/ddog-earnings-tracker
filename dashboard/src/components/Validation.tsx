import { summary } from "../data";
import { Annotation } from "./Annotation";

const wf = summary.walk_forward;
const ridge = wf.ridge;
const naive = wf.naive_persistence;
const rumOnly = wf.ridge_rum_lag1_only;
const npmAws = wf.ridge_npm_aws_lag1;
const ridgeRecent = wf.ridge_recent_window;
const naiveRecent = wf.naive_persistence_recent_window;

function rmsePp(value: number) {
  return `${(value * 100).toFixed(1)}pp`;
}

function metric(label: string, value: string, win?: boolean) {
  return (
    <div className={`rounded border px-2.5 py-2 ${win ? "border-brass-600/40 bg-brass-500/[0.07]" : "border-zinc-800"}`}>
      <p className="font-mono text-[10px] uppercase tracking-wider text-zinc-500">{label}</p>
      <p className="mt-1 font-mono text-sm text-zinc-100">{value}</p>
    </div>
  );
}

export function Validation() {
  return (
    <div className="h-full rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <h2 className="text-sm font-medium text-zinc-200">Walk-forward honesty</h2>
      <p className="mt-0.5 text-[12px] text-zinc-500">
        All {ridge.n_test} expanding-window forecasts · persistence still wins on RMSE
      </p>

      <div className="mt-4 space-y-3">
        <div>
          <p className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-zinc-500">
            Persistence baseline
          </p>
          <div className="grid grid-cols-2 gap-1.5">
            {metric("RMSE", `${(naive.rmse * 100).toFixed(1)}pp`, true)}
            {metric("MAPE", naive.mape.toFixed(3), true)}
          </div>
        </div>
        <div>
          <p className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-zinc-500">
            Ridge (both lag-1)
          </p>
          <div className="grid grid-cols-2 gap-1.5">
            {metric("RMSE", `${(ridge.rmse * 100).toFixed(1)}pp`)}
            {metric("MAPE", ridge.mape.toFixed(3))}
          </div>
        </div>
        <p className="font-mono text-[11px] text-zinc-500">
          RUM-only ridge RMSE {rmsePp(rumOnly.rmse)}. npm+AWS lag-1 RMSE {rmsePp(npmAws.rmse)} — closer, still behind persistence.
        </p>
        {ridgeRecent && naiveRecent ? (
          <p className="font-mono text-[11px] text-zinc-500">
            Recent {ridgeRecent.n_test}q window ({wf.recent_window_quarters[0]}–{wf.recent_window_quarters.at(-1)}):
            ridge {rmsePp(ridgeRecent.rmse)} vs persistence {rmsePp(naiveRecent.rmse)}.
          </p>
        ) : null}
      </div>

      <div className="mt-4 space-y-2 border-t border-zinc-800/80 pt-3">
        <Annotation
          label={`Ridge ${rmsePp(ridge.rmse)} RMSE. Adding AWS as a lag-1 control cuts that to ${rmsePp(npmAws.rmse)}. Persistence remains best at ${rmsePp(naive.rmse)}. Tracker, not alpha.`}
        />
        <Annotation
          label={`Sign-of-growth hit is ${ridge.directional_hit_rate.toFixed(2)} because YoY stayed positive. Change-direction hit is ${ridge.directional_change_hit_rate.toFixed(2)} — not evidence of timing skill.`}
        />
      </div>
    </div>
  );
}
