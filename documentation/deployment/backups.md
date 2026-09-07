# Backups

Create encrypted PostgreSQL logical backups with `pg_dump`, copy private storage and model packages with checksums, and retain the Alembic revision with every backup. Test restoration into an isolated database using `pg_restore`, run `alembic current`, verify ownership/media access, and record the exercise. No automatic remote backup service is included.
