#!/usr/bin/env python3
"""DDOG alternative-data prototype: SEC fundamentals + public npm adoption.

Public, legally accessible sources only.
Run from repo root: python3 src/analyze_ddog.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ddog_tracker.pipeline import run  # noqa: E402


if __name__ == "__main__":
    run()
