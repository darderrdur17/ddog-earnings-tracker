#!/usr/bin/env bash
# Create venv, install Python and dashboard dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
npm --prefix dashboard install
echo "Setup complete. Next: ./scripts/analyze.sh then ./scripts/dashboard.sh"
