# Alembic migrations

Run commands from `backend`, or use the root PowerShell wrappers.

```powershell
.\scripts\show-migration-status.ps1
.\scripts\migrate-database.ps1
.\scripts\downgrade-database.ps1 -Revision 0001_initial_schema
```

`0001_initial_schema` reproduces the unmanaged legacy schema. `0002_integrity_indexes` adds the audited feedback foreign key and targeted analysis indexes. Both have downgrade logic. Migration URLs come from application configuration; `alembic.ini` contains no credentials.

For a new change: update models, generate or write a revision, manually review types/nullability/defaults/keys/indexes/cascades, migrate an empty database, downgrade and re-upgrade it, then run the drift test. Autogeneration is guidance, not acceptance.

An existing unmanaged SQLite file must first be backed up and audited. If it exactly matches the legacy baseline, explicitly run `alembic stamp 0001_initial_schema`, then `alembic upgrade head`. Stamping asserts schema state; it does not alter application rows. Never stamp an unknown schema.

The drift check compares reflected migrated SQLite schema to registered metadata. PostgreSQL integration additionally checks the actual migration, but dialect-specific server defaults may still require manual review.
