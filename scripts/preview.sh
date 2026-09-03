#!/usr/bin/env bash
# Serve the last production build locally.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/dashboard"
npm run preview -- --host 127.0.0.1 --port 4173
