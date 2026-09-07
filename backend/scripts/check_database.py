#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check safe DeepSight database readiness.")
    parser.add_argument("--require-head", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        from app.core.database import (
            check_database_connection,
            engine,
            safe_database_target,
        )

        check_database_connection()
        if args.require_head:
            from alembic.script import ScriptDirectory
            from app.database.migrations import current_revision, get_alembic_config

            expected = ScriptDirectory.from_config(get_alembic_config()).get_current_head()
            if current_revision(engine) != expected:
                print("Database connection succeeded, but the schema is not at the Alembic head revision.")
                return 2
        print(f"Database ready: {safe_database_target()}.")
        return 0
    except Exception as error:
        target = "configured database"
        try:
            from app.core.database import safe_database_target

            target = safe_database_target()
        except Exception:
            pass
        print(f"Database connection failed for {target}: {error.__class__.__name__}.")
        return 1
    finally:
        if "engine" in locals():
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
