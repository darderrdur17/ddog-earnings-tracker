import { summary } from "../data";

export function Header() {
  const asOf = new Date(summary.as_of_utc);
  const asOfLabel = asOf.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  });

  return (
    <header className="flex flex-col gap-4 border-b border-zinc-800/80 pb-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-brass-500">
          Alternative data · Datadog (NASDAQ: DDOG)
        </p>
        <h1 className="mt-1.5 text-[1.85rem] font-semibold tracking-tight text-zinc-100">
          Earnings Tracker
        </h1>
        <p className="mt-2 max-w-2xl text-[13px] leading-relaxed text-zinc-400">
          A public-data pre-earnings read: npm as a coincident nowcast, AWS as a
          cloud-regime control, Wikipedia as a failed attention check. The
          lag-1 ridge is the call. Persistence still wins — that is shown on
          purpose. Not billable usage, not investment advice.
        </p>
        <p className="mt-2 font-mono text-[11px] text-zinc-500">
          Generated {asOfLabel}. Refresh:{" "}
          <span className="text-zinc-300">./scripts/analyze.sh</span> then{" "}
          <span className="text-zinc-300">./scripts/build.sh</span>.{" "}
          <a className="text-brass-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-300" href="/slides.html">
            10-slide talk
          </a>
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] text-zinc-500">
        <span className="rounded border border-zinc-800 bg-ink-900 px-2 py-1">
          NASDAQ: DDOG
        </span>
        <span className="rounded border border-zinc-800 bg-ink-900 px-2 py-1">
          As of {asOfLabel}
        </span>
        <span className="rounded border border-zinc-800 bg-ink-900 px-2 py-1">
          npm through {summary.npm_end}
        </span>
        <span className="rounded border border-zinc-800 bg-ink-900 px-2 py-1">
          AWS + wiki ingested
        </span>
        <span className="rounded border border-brass-600/40 bg-brass-500/10 px-2 py-1 text-brass-400">
          Confidence: exploratory
        </span>
      </div>
    </header>
  );
}
