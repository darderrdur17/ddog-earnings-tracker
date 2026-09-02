#!/usr/bin/env python3
"""Copy outputs/analysis_summary.json into dashboard/src for the Vite bake."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ddog_tracker.config import default_settings  # noqa: E402
from ddog_tracker.intra_quarter import sync_dashboard_summary  # noqa: E402

if __name__ == "__main__":
    settings = default_settings(ROOT)
    src = settings.out_dir / "analysis_summary.json"
    if not src.exists():
        raise SystemExit("Run python3 src/analyze_ddog.py first.")
    sync_dashboard_summary(settings)
    print(f"Copied {src} → dashboard/src/analysis_summary.json")
