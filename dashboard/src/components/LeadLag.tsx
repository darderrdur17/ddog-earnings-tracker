import { LEAD_LAG_SIGNALS, leadLag } from "../data";
import { Annotation } from "./Annotation";

const lags = [0, 1, 2, 3, 4];

function cell(signal: string, lag: number) {
  return leadLag.find((r) => r.signal === signal && r.lag === lag);
}

function tone(corr: number) {
  const a = Math.max(0.12, Math.min(0.75, Math.abs(corr)));
  if (corr < 0) {
    return { background: `rgba(113, 113, 122, ${a})`, color: "#e8eaef" };
  }
  return { background: `rgba(196, 165, 116, ${a})`, color: corr > 0.55 ? "#111318" : "#e8eaef" };
}

function fmt(corr: number) {
  return corr.toFixed(2);
}

export function LeadLag() {
  return (
    <div className="h-full rounded-lg border border-zinc-800/90 bg-ink-900 p-4">
      <h2 className="text-sm font-medium text-zinc-200">Lead–lag (signal YoY vs revenue YoY)</h2>
      <p className="mt-0.5 text-[12px] text-zinc-500">
        Lag 0 is a coincident nowcast. Lag 1 is the validated call. AWS is a quarterly macro control, not high-frequency.
      </p>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[280px] border-collapse text-center font-mono text-[11px]">
          <thead>
            <tr className="text-zinc-500">
              <th className="pb-2 text-left font-medium">Signal</th>
              {lags.map((lag) => (
                <th key={lag} className="pb-2 font-medium">
                  {lag}q
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {LEAD_LAG_SIGNALS.map((signal) => (
              <tr key={signal}>
                <td className="py-1 pr-2 text-left text-zinc-400">{signal}</td>
                {lags.map((lag) => {
                  const row = cell(signal, lag);
                  if (!row || row.corr == null) return <td key={lag} />;
                  return (
                    <td key={lag} className="p-0.5">
                      <div
                        className="rounded px-1 py-1.5 tabular-nums transition-transform duration-200 hover:scale-[1.04]"
                        style={tone(row.corr)}
                        title={`n=${row.n}`}
                      >
                        {row.corr.toFixed(2)}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 space-y-2">
        <Annotation
          label={`RUM is a coincident nowcast (${fmt(cell("RUM", 0)?.corr ?? 0)}); lag-1 is weaker (${fmt(cell("RUM", 1)?.corr ?? 0)}). Do not call lag-0 a leading indicator. AWS lag-1 is ${fmt(cell("AWS", 1)?.corr ?? 0)} — a macro control, not DDOG usage.`}
        />
        <Annotation
          label={`Wiki DDOG is not coincident (${fmt(cell("Wiki DDOG", 0)?.corr ?? 0)}); lag-2 is ${fmt(cell("Wiki DDOG", 2)?.corr ?? 0)}. New Relic wiki is negative — not generic observability traffic.`}
        />
      </div>
    </div>
  );
}
