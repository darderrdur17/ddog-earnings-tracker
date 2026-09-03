import { LAST_YOY, pct, summary } from "../data";

const intra = summary.intra_quarter;
const guide = intra.management_guidance;

export function CallBanner() {
  const ridge = summary.latest_estimate.pred;
  const print = LAST_YOY;
  const mid = guide.implied_yoy_mid;
  const tracking = summary.latest_estimate.tracking;

  return (
    <section
      aria-label="2026Q3 call stack"
      className="mt-5 rounded-lg border border-zinc-800/90 bg-ink-900"
    >
      <div className="flex flex-col gap-3 border-b border-zinc-800/80 px-4 py-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-brass-500">
            01 · How the signals become a call
          </p>
          <h2 className="mt-1 text-[15px] font-medium text-zinc-100">
            {summary.latest_estimate.quarter} is tracking {tracking} last print
          </h2>
        </div>
        <p className="max-w-xl text-[12px] leading-relaxed text-zinc-500">
          Ahead / behind is ±1pp versus last reported YoY, not Street. Ridge uses
          prior-quarter npm only. Stub and 8-K sit beside it as checks.
        </p>
      </div>
      <div className="grid divide-y divide-zinc-800/80 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
        <Baseline
          kicker="Last print"
          value={pct(print)}
          meta={`${summary.latest_estimate.last_reported_quarter} · persistence`}
        />
        <Baseline
          kicker="Validated call"
          value={pct(ridge)}
          meta={`Lag-1 ridge · ${tracking}`}
          accent
        />
        <Baseline
          kicker="Company 8-K"
          value={mid == null ? "n/a" : pct(mid)}
          meta={
            guide.available
              ? `Midpoint of $${(guide.revenue_low / 1e9).toFixed(3)}–${(guide.revenue_high / 1e9).toFixed(3)}bn`
              : "No guidance ingested"
          }
        />
      </div>
    </section>
  );
}

function Baseline({
  kicker,
  value,
  meta,
  accent,
}: {
  kicker: string;
  value: string;
  meta: string;
  accent?: boolean;
}) {
  return (
    <div className={`px-4 py-4 ${accent ? "bg-brass-500/[0.05]" : ""}`}>
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">{kicker}</p>
      <p className="mt-2 font-mono text-[1.85rem] font-medium leading-none tracking-tight text-zinc-100">
        {value}
      </p>
      <p className="mt-2 text-[12px] text-zinc-500">{meta}</p>
    </div>
  );
}
