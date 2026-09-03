#!/usr/bin/env bash
# Unit tests for collectors, features, and walk-forward leakage guards.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/pytest ]]; then
  .venv/bin/pytest tests -q
else
  python3 -m pytest tests -q
fi
