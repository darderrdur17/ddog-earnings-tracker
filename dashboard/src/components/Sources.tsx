import { summary } from "../data";

type Props = { asOf: string; npmEnd: string };

export function Sources({ asOf, npmEnd }: Props) {
  return (
    <footer className="mt-8 border-t border-zinc-800/80 pt-5 pb-10">
      <p className="mb-4 font-mono text-[10px] uppercase tracking-[0.16em] text-brass-500">
        04 · Public sources and limits
      </p>
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">Freshness</h3>
          <ul className="mt-2 space-y-1 text-[12px] text-zinc-500">
            <li>npm downloads: daily (through {npmEnd})</li>
            <li>SEC DDOG revenue: on 10-Q / 10-K filing</li>
            <li>AWS / GCP / MSFT IC: SEC XBRL segment facts on filing</li>
            <li>Wikipedia pageviews: monthly official API</li>
            <li>Hiring: not ingested (licensed boards only)</li>
            <li>Generated: {asOf}</li>
            <li>Refresh: ./scripts/analyze.sh then ./scripts/build.sh</li>
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href="/slides.html">
                10-slide talk (same story as the report)
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">Sources</h3>
          <ul className="mt-2 space-y-1 text-[12px] text-zinc-500">
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href={summary.sources.sec}>
                SEC Company Facts CIK0001561550
              </a>
            </li>
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href={summary.sources.npm}>
                npm downloads range API
              </a>
            </li>
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href={summary.sources.sec_xbrl}>
                SEC EDGAR XBRL (AWS, Google Cloud, Intelligent Cloud)
              </a>
            </li>
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href={summary.sources.wikimedia}>
                Wikimedia pageviews API (Datadog, New Relic placebo)
              </a>
            </li>
            <li>
              <a className="text-zinc-400 underline decoration-zinc-700 underline-offset-2 hover:text-brass-400" href="https://www.sec.gov/Archives/edgar/data/1561550/000162828026053829/ex-991x20260630x8k.htm">
                8-K Exhibit 99.1 (6 Aug 2026) Q3 2026 company outlook
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">Limitations</h3>
          <p className="mt-2 text-[12px] leading-relaxed text-zinc-500">{summary.caveat}</p>
          <p className="mt-2 text-[12px] leading-relaxed text-zinc-500">
            Google Trends was not scraped (no official public API). Wikipedia is the ToS-safe attention series. Hiring remains licensed-only.
          </p>
        </div>
      </div>
    </footer>
  );
}
