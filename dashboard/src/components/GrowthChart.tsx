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
import { growthSeries } from "../data";
import { Annotation } from "./Annotation";

function tip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="mb-1 font-mono text-[11px] text-zinc-400">{label}</p>
      {payload
        .filter((p) => p.value != null)
        .map((p) => (
          <p key={p.name} className="font-mono text-[11px]" style={{ color: p.color }}>
            {p.name} {Number(p.value).toFixed(1)}%
          </p>
        ))}
    </div>
  );
}

export function GrowthChart() {
  return (
    <div className="rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-sm font-medium text-zinc-200">Revenue YoY vs walk-forward calls</h2>
          <p className="mt-0.5 text-[12px] text-zinc-500">
            Reported growth, ridge (lag-1 npm), persistence baseline. Model quarterly; npm daily.
          </p>
        </div>
        <Annotation label="Notice the 2026 acceleration: actual 35.6% vs ridge 28.6% in 2026Q2. Lag-1 npm missed the print." />
      </div>
      <div className="h-[280px] w-full">
        <ResponsiveContainer>
          <LineChart data={growthSeries} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="quarter" tickLine={false} axisLine={false} interval={1} />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `${v.toFixed(0)}%`}
              domain={[20, 40]}
            />
            <Tooltip content={tip} />
            <Legend
              wrapperStyle={{ fontSize: 11, color: "#a1a1aa" }}
              formatter={(v) => <span className="text-zinc-400">{v}</span>}
            />
            <Line
              type="monotone"
              dataKey="reported"
              name="Reported YoY"
              stroke="#e8eaef"
              strokeWidth={2}
              dot={false}
              animationDuration={1100}
            />
            <Line
              type="monotone"
              dataKey="ridge"
              name="Ridge (lag-1)"
              stroke="#c4a574"
              strokeWidth={1.75}
              strokeDasharray="4 3"
              dot={false}
              connectNulls={false}
              animationDuration={1300}
            />
            <Line
              type="monotone"
              dataKey="persistence"
              name="Persistence"
              stroke="#71717a"
              strokeWidth={1.5}
              dot={false}
              connectNulls={false}
              animationDuration={1500}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
