import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { LAST_REVENUE, LAST_YOY, moneyM, pct, pp, summary } from "../data";
import { Annotation } from "./Annotation";

const tiles = [
  { key: "rev", delay: 0.05 },
  { key: "yoy", delay: 0.12 },
  { key: "est", delay: 0.19 },
  { key: "track", delay: 0.26 },
] as const;

function RevenueTile() {
  return (
    <KpiShell
      label="Last reported revenue"
      value={moneyM(LAST_REVENUE)}
      meta={`${summary.latest_estimate.last_reported_quarter} · SEC Company Facts`}
      note="Q4 is FY residual when no Q4 frame exists. Latest print is a 10-Q frame."
    />
  );
}

function YoyTile() {
  return (
    <KpiShell
      label="Reported revenue YoY"
      value={pct(LAST_YOY)}
      meta={`${summary.latest_estimate.last_reported_quarter} vs prior year`}
      note="This is the persistence baseline: last observed growth, carried forward."
    />
  );
}

function EstimateTile() {
  return (
    <KpiShell
      label="Lag-1 ridge (validated)"
      value={pct(summary.latest_estimate.pred)}
      meta={`${summary.latest_estimate.quarter} · prior-quarter npm only`}
      note="Validated lag-1 model. RUM coincident correlation is stronger; that is a nowcast, not a lead."
    />
  );
}

function TrackingTile() {
  const delta = summary.latest_estimate.delta_vs_baseline;
  return (
    <KpiShell
      label="Tracking vs persistence"
      value={
        <span className="inline-flex items-center gap-2.5">
          <span className="status-pulse inline-block h-2 w-2 rounded-full bg-brass-500" />
          <span className="capitalize">{summary.latest_estimate.tracking}</span>
        </span>
      }
      meta={`${pp(delta)} vs last reported ${pct(LAST_YOY)}`}
      note="Behind: estimate is at least 1pp below last reported YoY. Ahead is the symmetric case."
      emphasize
    />
  );
}

function KpiShell({
  label,
  value,
  meta,
  note,
  emphasize,
}: {
  label: string;
  value: ReactNode;
  meta: string;
  note: string;
  emphasize?: boolean;
}) {
  return (
    <article
      className={`flex h-full flex-col justify-between rounded-lg border px-4 py-3.5 ${
        emphasize
          ? "border-brass-600/35 bg-brass-500/[0.06]"
          : "border-zinc-800/90 bg-ink-900"
      }`}
    >
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">{label}</p>
        <p className="mt-2 font-mono text-[1.7rem] font-medium leading-none tracking-tight text-zinc-100">
          {value}
        </p>
        <p className="mt-2 text-[12px] text-zinc-500">{meta}</p>
      </div>
      <Annotation className="mt-3" label={note} />
    </article>
  );
}

export function KpiRow() {
  return (
    <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {tiles.map((tile) => (
        <motion.div
          key={tile.key}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: tile.delay, ease: [0.22, 1, 0.36, 1] }}
        >
          {tile.key === "rev" && <RevenueTile />}
          {tile.key === "yoy" && <YoyTile />}
          {tile.key === "est" && <EstimateTile />}
          {tile.key === "track" && <TrackingTile />}
        </motion.div>
      ))}
    </div>
  );
}
