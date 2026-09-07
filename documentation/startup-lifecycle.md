# Startup Lifecycle

DeepSight separates four operations that were previously mixed together.

## 1. Application import and startup

`import app.main` constructs the FastAPI route graph only. It does not connect to or create SQLite, create tables, create/update users, seed entitlements, initialize Firebase, create runtime directories/reports, or load PyTorch checkpoints and InsightFace.

The FastAPI lifespan configures consistent logging and records startup/shutdown state without secrets. Inference components remain lazy until the first inference request. The request-ID middleware accepts or creates `X-Request-ID`, returns it in the response, and writes method/path/status/duration only.

## 2. Database initialization

```powershell
.\.venv\Scripts\python.exe backend\scripts\init_database.py
```

This explicitly registers ORM models and calls SQLAlchemy table creation. It is a temporary SQLite foundation mechanism until the authorized PostgreSQL/Alembic phase. Production execution requires `--confirm-production`.

## 3. Development reference-data seed

```powershell
.\.venv\Scripts\python.exe backend\scripts\seed_development.py
```

This idempotent command is blocked unless `APP_ENV=development`. Plans are currently code-defined, so it reports them unchanged and writes no database rows. It never creates users, histories, analyses, payments, or performance metrics.

## 4. Administrator creation

```powershell
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com
```

This is the only foundation command that creates an administrator. It is interactive, hashes a strong password, refuses existing users by default, and has an explicit `--update-existing` path.

## Model lifecycle and health

The model catalog checks only checkpoint existence. PyTorch/timm, preprocessing code, checkpoints, and InsightFace are reached lazily by inference services. Cached models load once per process. Health reports `not_loaded`, `loaded`, or `disabled`, never a private path. Load errors become controlled inference failures and are logged without media or secrets.
