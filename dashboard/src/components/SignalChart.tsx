import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TooltipProps } from "recharts";
import { signalSeries } from "../data";
import { Annotation } from "./Annotation";

function tip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="mb-1 font-mono text-[11px] text-zinc-400">{label}</p>
      {payload
        .filter((p) => p.value != null && Number.isFinite(Number(p.value)))
        .map((p) => (
        <p key={p.name} className="font-mono text-[11px]" style={{ color: p.color }}>
          {p.name} {Number(p.value).toFixed(1)}%
        </p>
      ))}
    </div>
  );
}

export function SignalChart() {
  return (
    <div className="rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-sm font-medium text-zinc-200">npm + AWS control vs revenue YoY</h2>
          <p className="mt-0.5 text-[12px] text-zinc-500">
            Same-quarter match. AWS is SEC XBRL segment revenue (macro), not Datadog accounts.
          </p>
        </div>
        <Annotation label="RUM tracks the level of growth. AWS YoY is the cloud-spend regime. Wiki pageviews are omitted here — 2025 spikes would squash the scale." />
      </div>
      <div className="h-[280px] w-full">
        <ResponsiveContainer>
          <LineChart data={signalSeries} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="quarter" tickLine={false} axisLine={false} interval={1} />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `${v.toFixed(0)}%`}
            />
            <Tooltip content={tip} />
            <Legend
              wrapperStyle={{ fontSize: 11 }}
              formatter={(v) => <span className="text-zinc-400">{v}</span>}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              name="Revenue YoY"
              stroke="#e8eaef"
              strokeWidth={2}
              dot={false}
              animationDuration={1100}
            />
            <Line
              type="monotone"
              dataKey="rum"
              name="RUM downloads YoY"
              stroke="#c4a574"
              strokeWidth={1.75}
              dot={false}
              animationDuration={1300}
            />
            <Line
              type="monotone"
              dataKey="aws"
              name="AWS segment YoY"
              stroke="#94a3b8"
              strokeWidth={1.25}
              strokeDasharray="3 3"
              dot={false}
              connectNulls={false}
              animationDuration={1600}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
