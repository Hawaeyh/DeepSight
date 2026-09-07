#!/usr/bin/env python3
"""Inspect or release only stale reserved image-analysis usage entries."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal
from app.models.subscription import DetectionUsage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older-than-minutes", type=int, default=30)
    parser.add_argument("--confirm", action="store_true")
    arguments = parser.parse_args()
    if arguments.older_than_minutes < 1:
        parser.error("--older-than-minutes must be positive")
    cutoff = datetime.utcnow() - timedelta(minutes=arguments.older_than_minutes)
    with SessionLocal() as db:
        rows = db.query(DetectionUsage).filter(
            DetectionUsage.media_type == "image",
            DetectionUsage.status == "reserved",
            DetectionUsage.created_at < cutoff,
        ).all()
        print(f"stale image reservations: {len(rows)}")
        if not arguments.confirm:
            print("dry-run only; add --confirm to release these reservations")
            return 0
        now = datetime.utcnow()
        for row in rows:
            row.status = "released"
            row.released_at = now
        db.commit()
        print(f"released image reservations: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
