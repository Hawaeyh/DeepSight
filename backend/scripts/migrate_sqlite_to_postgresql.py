#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import MetaData, create_engine, func, inspect, select, text
from sqlalchemy.engine import make_url


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


MIGRATION_ORDER = [
    "users",
    "account_entitlements",
    "analysis",
    "analysis_feedback",
    "detection_usage",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Explicitly copy current DeepSight SQLite rows to migrated PostgreSQL."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination-env", default="DATABASE_URL")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--confirm-migration",
        action="store_true",
        help="Required for writes. Destination tables must be empty.",
    )
    parser.add_argument("--report", type=Path, default=Path("migration_report.json"))
    return parser.parse_args()


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def table_counts(connection, metadata: MetaData) -> dict[str, int]:
    return {
        table_name: int(
            connection.execute(
                select(func.count()).select_from(metadata.tables[table_name])
            ).scalar_one()
        )
        for table_name in MIGRATION_ORDER
    }


def main() -> int:
    args = parse_args()
    source_path = args.source.expanduser().resolve()
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "dry-run" if args.dry_run else "migration",
        "duplicate_policy": "fail-and-rollback",
        "source": {"type": "sqlite", "row_counts": {}},
        "destination": {"type": "not_checked", "row_counts_before": {}, "row_counts_after": {}},
        "tables": {},
        "warnings": [],
        "success": False,
    }

    if not source_path.is_file():
        print(f"Source SQLite file does not exist: {source_path}")
        return 2

    source_engine = create_engine(f"sqlite:///{source_path.as_posix()}")
    destination_engine = None
    try:
        source_tables = set(inspect(source_engine).get_table_names())
        missing_source = set(MIGRATION_ORDER) - source_tables
        if missing_source:
            raise RuntimeError(
                "Source is missing required tables: " + ", ".join(sorted(missing_source))
            )
        source_metadata = MetaData()
        source_metadata.reflect(bind=source_engine, only=MIGRATION_ORDER)
        with source_engine.connect() as source_connection:
            source_counts = table_counts(source_connection, source_metadata)
        report["source"]["row_counts"] = source_counts

        destination_value = os.getenv(args.destination_env)
        destination_url = make_url(destination_value) if destination_value else None
        destination_is_postgresql = bool(
            destination_url and destination_url.drivername == "postgresql+psycopg"
        )
        if destination_is_postgresql:
            destination_engine = create_engine(destination_url, pool_pre_ping=True)
            destination_tables = set(inspect(destination_engine).get_table_names())
            missing_destination = set(MIGRATION_ORDER) - destination_tables
            if missing_destination:
                raise RuntimeError(
                    "Destination must be upgraded through Alembic first; missing tables: "
                    + ", ".join(sorted(missing_destination))
                )
            destination_metadata = MetaData()
            destination_metadata.reflect(bind=destination_engine, only=MIGRATION_ORDER)
            with destination_engine.connect() as destination_connection:
                before_counts = table_counts(destination_connection, destination_metadata)
            report["destination"] = {
                "type": "postgresql",
                "row_counts_before": before_counts,
                "row_counts_after": before_counts.copy(),
            }
        else:
            destination_metadata = None
            before_counts = {}
            report["warnings"].append(
                f"{args.destination_env} was missing or was not postgresql+psycopg; destination was not checked."
            )

        for table_name in MIGRATION_ORDER:
            report["tables"][table_name] = {
                "source_rows": source_counts[table_name],
                "destination_before": before_counts.get(table_name),
                "inserted": 0,
                "skipped": 0,
                "failed": 0,
            }

        if args.dry_run:
            report["success"] = True
            write_report(args.report, report)
            print(f"Dry run complete. Report: {args.report}")
            return 0

        if not args.confirm_migration:
            raise RuntimeError("Writes require --confirm-migration.")
        if not destination_is_postgresql or destination_engine is None or destination_metadata is None:
            raise RuntimeError("A postgresql+psycopg destination is required for migration.")
        if any(before_counts.values()):
            raise RuntimeError(
                "Destination migration tables are not empty; no rows were written."
            )

        with source_engine.connect() as source_connection, destination_engine.begin() as destination_connection:
            for table_name in MIGRATION_ORDER:
                source_table = source_metadata.tables[table_name]
                destination_table = destination_metadata.tables[table_name]
                rows = [dict(row._mapping) for row in source_connection.execute(select(source_table))]
                if rows:
                    destination_connection.execute(destination_table.insert(), rows)
                report["tables"][table_name]["inserted"] = len(rows)

            for table_name in MIGRATION_ORDER:
                destination_connection.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM \"{table_name}\"), 1), "
                        f"(SELECT COUNT(*) > 0 FROM \"{table_name}\"))"
                    ),
                    {"table_name": table_name},
                )

        with destination_engine.connect() as destination_connection:
            after_counts = table_counts(destination_connection, destination_metadata)
        report["destination"]["row_counts_after"] = after_counts
        mismatches = {
            table: {"source": source_counts[table], "destination": after_counts[table]}
            for table in MIGRATION_ORDER
            if source_counts[table] != after_counts[table]
        }
        if mismatches:
            report["row_count_mismatches"] = mismatches
            raise RuntimeError("Post-migration row counts differ.")

        report["success"] = True
        write_report(args.report, report)
        print(f"Migration complete and row counts verified. Report: {args.report}")
        return 0
    except Exception as error:
        report["error"] = error.__class__.__name__
        safe_message = str(error) if isinstance(error, RuntimeError) else "Database operation failed; inspect server logs."
        report["error_message"] = safe_message
        write_report(args.report, report)
        print(f"Migration failed safely ({error.__class__.__name__}): {safe_message}")
        print(f"Failure report: {args.report}")
        return 1
    finally:
        source_engine.dispose()
        if destination_engine is not None:
            destination_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
