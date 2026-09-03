#!/usr/bin/env bash
# Regenerate Word (.docs) copies from docs/*.md (requires pandoc).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="${ROOT}/docs"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required. Install: brew install pandoc" >&2
  exit 1
fi

for md in "${DOCS}"/*.md; do
  base="$(basename "${md}" .md)"
  out="${DOCS}/${base}.docs"
  pandoc "${md}" -o "${out}" --from markdown --to docx
  echo "Wrote ${out}"
done
