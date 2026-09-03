#!/usr/bin/env bash
# Build ddog_takehome_submission.zip aligned with take-home deliverables:
#   1. Written report (docs/report.md + report.docs)
#   2. Ten-slide deck (docs/slides.html)
#   3. Annotated dashboard prototype (dashboard/)
#   4. Optional code (src/, tests/, scripts/, data/, outputs/)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="${ROOT}/ddog_takehome_submission.zip"
PKG="ddog_takehome_submission"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/ddog_pkg.XXXXXX")"
DEST="${STAGE}/${PKG}"

cleanup() { rm -rf "${STAGE}"; }
trap cleanup EXIT

echo "==> Sync dashboard summary"
if [[ -f outputs/analysis_summary.json ]]; then
  python3 scripts/sync_dashboard_summary.py 2>/dev/null || true
fi

echo "==> Regenerate Word copies (docs/*.docs)"
if command -v pandoc >/dev/null 2>&1; then
  ./scripts/export_docs.sh
else
  echo "    (skip: pandoc not installed)"
fi

echo "==> Run tests"
./scripts/test.sh

echo "==> Stage submission folder"
mkdir -p "${DEST}"

# Full project (minus heavy / local-only paths)
rsync -a \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '.cursor' \
  --exclude '.vercel' \
  --exclude '.pytest_cache' \
  --exclude '**/.DS_Store' \
  --exclude '**/node_modules' \
  --exclude 'dashboard/dist' \
  --exclude 'dashboard/.vercel' \
  --exclude 'data/cache' \
  --exclude 'outputs/*.log' \
  --exclude 'ddog_takehome_submission.zip' \
  --exclude "${STAGE}" \
  --exclude '.Rhistory' \
  --exclude '**/*.tsbuildinfo' \
  --exclude 'Take-Home_Assignment*.md' \
  "${ROOT}/" "${DEST}/"

# Top-level copies so reviewers see deliverables immediately
cp "${ROOT}/docs/report.md" "${DEST}/report.md"
cp "${ROOT}/docs/report.docs" "${DEST}/report.docs"
cp "${ROOT}/docs/slides.html" "${DEST}/slides.html"

echo "==> Zip"
rm -f "${OUT}"
(
  cd "${STAGE}"
  zip -r "${OUT}" "${PKG}" \
    -x "**/.DS_Store" \
    -x "**/__pycache__/*" \
    -x "**/*.pyc"
)

echo ""
echo "Wrote ${OUT}"
ls -lh "${OUT}"
echo ""
echo "Deliverables inside ${PKG}/:"
echo "  report.md / report.docs     — written report"
echo "  slides.html                 — 10-slide deck"
echo "  dashboard/                  — annotated prototype"
echo "  docs/                       — full documentation"
echo "  src/ tests/ scripts/        — code"
echo "  SUBMISSION.md               — requirement mapping"
