# Administrator Setup

DeepSight no longer contains a default administrator, known password, automatic user seed, or import-time role mutation.

## Create a local administrator

Initialize the schema first, then run the interactive command:

```powershell
.\.venv\Scripts\python.exe backend\scripts\init_database.py
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com
```

The command validates the email, reads the password twice without echo, requires at least 12 characters plus lowercase, uppercase, number, and symbol, enforces bcrypt's 72-byte limit, hashes with the existing bcrypt helper, and prints no password.

If the email exists, the command exits non-zero and changes nothing. To deliberately replace that user's password, activate the account, and assign the administrator role:

```powershell
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com --update-existing
```

Treat `--update-existing` as a credential-reset operation and use it only with authorization.

## Firebase limitation

This command creates a local SQLite user for the current local JWT authentication implementation. It does not create, update, or verify a Firebase Authentication identity. That integration remains a later authentication phase.

## Production safety

There is no hard-coded email, password, UID, or secret key. Production initialization requires explicit operational procedures and is not authorized by the current foundation phase.
