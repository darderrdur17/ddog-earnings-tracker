#!/usr/bin/env bash
# Production-style static build of the dashboard.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
npm --prefix dashboard run build
echo "Built dashboard/dist. Preview: ./scripts/preview.sh"
