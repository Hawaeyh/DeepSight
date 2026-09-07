# Database architecture

PostgreSQL 17 with the `postgresql+psycopg` driver is the recommended development and deployment database. SQLite remains supported for isolated tests, offline development, and as a legacy export source.

`DATABASE_URL` is validated by application settings, passed to one SQLAlchemy engine per process, and used by a request-scoped session dependency. PostgreSQL alone receives pool sizing, overflow, recycle, pre-ping, and connection-timeout options. SQLite alone receives its thread option and foreign-key pragma.

Alembic is the schema authority. Importing the application never creates tables, migrates data, seeds rows, or creates an administrator. All models are registered through `app.database.initialization.register_models`.

Current identifiers remain integer primary keys. Email remains a unique account/entitlement identifier. No analysis-owner key is introduced in this phase.

## Time strategy

New architecture should store UTC, timezone-aware values and convert only at presentation boundaries. The legacy schema mixes a timezone-aware `users.created_at` declaration with naïve UTC application timestamps elsewhere. Changing all persisted timestamp semantics now risks compatibility, so this phase preserves the columns and documents a later audited data migration.

## Compatibility changes

- Stable names are configured for indexes and PK/FK/unique/check constraints.
- SQLite foreign-key enforcement is enabled per connection.
- Feedback now has a validated cascading foreign key to analysis.
- Analysis date, result, type, and model-name access paths have indexes.
- No PostgreSQL enums or SQLite-only model types are used.
