# Development database reset

Reset is destructive and is never run by application startup.

```powershell
.\scripts\reset-development-database.ps1
```

The script accepts only `APP_ENV=development`, the psycopg driver, localhost, and a database named `deepsight`. It displays the target without a password and requires typing the exact confirmation phrase. It then recreates the public schema, runs Alembic, and invokes only the safe reference-data seed. It does not create administrators. Back up anything valuable first; dropped schema contents are recoverable only from a backup.
