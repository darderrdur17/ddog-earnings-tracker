#!/usr/bin/env bash
# Zip a reviewable packet (no venv, node_modules, cache, or git).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="${ROOT}/ddog_takehome_submission.zip"
rm -f "$OUT"
zip -r "$OUT" . \
  -x ".git/*" \
  -x ".venv/*" \
  -x "**/node_modules/*" \
  -x "data/cache/*" \
  -x "**/.DS_Store" \
  -x "dashboard/dist/*" \
  -x "dashboard/.vercel/*" \
  -x "*.pyc" \
  -x "**/__pycache__/*" \
  -x ".cursor/*" \
  -x ".vercel/*" \
  -x ".pytest_cache/*" \
  -x "outputs/pip.log" \
  -x "outputs/run.log" \
  -x ".Rhistory" \
  -x "ddog_takehome_submission.zip"
echo "Wrote $OUT"
ls -lh "$OUT"
