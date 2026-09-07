#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.services.cleanup_service import CleanupService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview or apply contained temporary-media cleanup.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        print(json.dumps(CleanupService.run(db, apply=args.confirm), indent=2, sort_keys=True))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
