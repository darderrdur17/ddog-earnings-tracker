#!/usr/bin/env bash
# Optional Python UI. Demo the Vite app instead for the interview.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/streamlit ]]; then
  ST=".venv/bin/streamlit"
else
  ST="streamlit"
fi
"$ST" run src/dashboard.py --server.headless true --server.port 8501
