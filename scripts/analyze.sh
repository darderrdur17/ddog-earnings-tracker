#!/usr/bin/env bash
# Refresh public data, rebuild the panel, and bake dashboard JSON.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/python ]]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi
"$PY" src/analyze_ddog.py
echo "Analysis written to outputs/. Dashboard JSON synced."
