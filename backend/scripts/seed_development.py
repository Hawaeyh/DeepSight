#!/usr/bin/env python3
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.services.subscription_service import PLANS  # noqa: E402


def main() -> int:
    if settings.APP_ENV != "development":
        print(f"Development seed blocked because APP_ENV={settings.APP_ENV}.")
        return 2

    # Plans are currently immutable code configuration, not database rows. Keeping
    # this explicit command makes that fact visible and avoids inventing records
    # before the planned PostgreSQL/Alembic plan-table migration.
    unchanged = len(PLANS)
    print("Development reference-data seed complete.")
    print("Inserted: 0")
    print("Updated: 0")
    print(f"Unchanged: {unchanged}")
    print("Subscription plans remain code-defined in app.services.subscription_service.")
    print("No users, analyses, payments, model metrics, or credentials were created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
