#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.database.migrations import current_revision, upgrade_database  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upgrade the configured DeepSight database through Alembic."
    )
    parser.add_argument("--revision", default="head")
    parser.add_argument("--confirm-production", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if settings.APP_ENV == "production" and not args.confirm_production:
        print("Refusing production migration without --confirm-production.")
        return 2
    try:
        upgrade_database(args.revision)
        print(f"Database migration complete. Current revision: {current_revision() or 'none'}")
        return 0
    except Exception as error:
        print(f"Database migration failed: {error.__class__.__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
