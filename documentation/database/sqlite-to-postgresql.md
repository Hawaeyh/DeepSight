# SQLite to PostgreSQL

No existing SQLite data is migrated automatically. Keep the source file and create a verified backup before proceeding.

1. Stop application writes and back up the SQLite file.
2. Run `python backend/scripts/audit_database_integrity.py --database-url sqlite:///...` and resolve reported problems without deleting rows automatically.
3. Create an empty PostgreSQL database and run `alembic upgrade head` against it.
4. Dry-run the copier:

```powershell
.\.venv\Scripts\python.exe backend\scripts\migrate_sqlite_to_postgresql.py `
  --source backend\deepsight.db --destination-env DATABASE_URL --dry-run `
  --report migration_report.json
```

5. Review counts/warnings, then rerun with `--confirm-migration` during a maintenance window.
6. Preserve both the source backup and report; verify the application against PostgreSQL before changing production configuration.

The order is users, entitlements, analyses, feedback, then usage. IDs, password hashes, and timestamps are copied unchanged. The destination must already be migrated and all migration tables must be empty. Any duplicate, constraint, insert, or count error rolls the transaction back. The duplicate policy is fail-and-rollback; rows are never silently skipped. The JSON report records source/destination counts, inserted/skipped/failed counts, and safe error categories. CSV is not produced because JSON is the implemented authoritative report.
