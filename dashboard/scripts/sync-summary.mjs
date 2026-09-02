import { copyFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const dashRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dest = resolve(dashRoot, "src/analysis_summary.json");
const src = resolve(dashRoot, "../outputs/analysis_summary.json");

if (existsSync(src)) {
  copyFileSync(src, dest);
  console.log("Copied ../outputs/analysis_summary.json → src/analysis_summary.json");
} else if (existsSync(dest)) {
  console.log("No ../outputs copy; using baked src/analysis_summary.json");
} else {
  console.error("Missing analysis_summary.json. Run: python3 src/analyze_ddog.py");
  process.exit(1);
}
