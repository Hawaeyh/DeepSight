#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import inspect, text


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import engine  # noqa: E402


EXPECTED_TABLES = {
    "users",
    "analysis",
    "analysis_feedback",
    "account_entitlements",
    "detection_usage",
}


def scalar(connection, query: str) -> int:
    return int(connection.execute(text(query)).scalar_one())


def run_audit() -> dict:
    inspector = inspect(engine)
    available = set(inspector.get_table_names())
    missing = sorted(EXPECTED_TABLES - available)
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dialect": engine.dialect.name,
        "missing_tables": missing,
        "row_counts": {},
        "issues": {},
    }
    with engine.connect() as connection:
        for table in sorted(EXPECTED_TABLES & available):
            report["row_counts"][table] = scalar(
                connection, f'SELECT COUNT(*) FROM "{table}"'
            )

        checks = {
            "orphan_feedback": """
                SELECT COUNT(*) FROM analysis_feedback f
                LEFT JOIN analysis a ON a.id = f.analysis_id
                WHERE a.id IS NULL
            """,
            "duplicate_user_emails_case_insensitive": """
                SELECT COUNT(*) FROM (
                    SELECT LOWER(email) FROM users
                    GROUP BY LOWER(email) HAVING COUNT(*) > 1
                ) duplicates
            """,
            "duplicate_entitlement_emails_case_insensitive": """
                SELECT COUNT(*) FROM (
                    SELECT LOWER(email) FROM account_entitlements
                    GROUP BY LOWER(email) HAVING COUNT(*) > 1
                ) duplicates
            """,
            "entitlements_without_users": """
                SELECT COUNT(*) FROM account_entitlements e
                LEFT JOIN users u ON LOWER(u.email) = LOWER(e.email)
                WHERE u.id IS NULL
            """,
            "invalid_roles": """
                SELECT COUNT(*) FROM users
                WHERE role IS NULL OR role NOT IN ('user', 'admin')
            """,
            "invalid_plans": """
                SELECT COUNT(*) FROM account_entitlements
                WHERE plan NOT IN ('starter', 'basic', 'lite')
            """,
            "invalid_entitlement_statuses": """
                SELECT COUNT(*) FROM account_entitlements
                WHERE status NOT IN ('active', 'inactive', 'cancelled')
            """,
            "analysis_missing_required_values": """
                SELECT COUNT(*) FROM analysis
                WHERE filename IS NULL OR file_path IS NULL OR file_type IS NULL
                   OR prediction IS NULL OR confidence IS NULL OR risk_level IS NULL
                   OR model_name IS NULL OR model_version IS NULL OR device IS NULL
                   OR processing_time IS NULL OR status IS NULL
            """,
        }
        if not missing:
            report["issues"] = {
                name: scalar(connection, query) for name, query in checks.items()
            }
    report["healthy"] = not missing and not any(report["issues"].values())
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit DeepSight database integrity.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = run_audit()
        serialized = json.dumps(report, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + "\n", encoding="utf-8")
            print(f"Integrity report written: {args.output}")
        else:
            print(serialized)
        return 0 if report["healthy"] else 1
    except Exception as error:
        print(f"Database integrity audit failed: {error.__class__.__name__}.")
        return 2
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
