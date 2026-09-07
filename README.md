# DeepSight System

DeepSight is an in-development deepfake media analysis platform with a React frontend, FastAPI backend, and Chrome Manifest V3 extension. PostgreSQL is the recommended database, Alembic controls schema, and SQLite remains available for tests and limited offline development.

The foundation is safe to import: importing `app.main` does not create tables, users, subscriptions, storage directories, or reports, and it does not load inference checkpoints or InsightFace. User analysis routes now enforce trusted local-JWT ownership and media is no longer publicly mounted. This does **not** make the application production-ready.

## Documentation

- [Local development](documentation/local-development.md)
- [Testing strategy](documentation/testing-strategy.md)
- [Administrator setup](documentation/administrator-setup.md)
- [Startup lifecycle](documentation/startup-lifecycle.md)
- [Foundation stabilisation](documentation/foundation-stabilisation.md)
- [Current system audit](documentation/current-system-audit.md)
- [Development roadmap](documentation/development-roadmap.md)
- [Database architecture](documentation/database/database-architecture.md)
- [PostgreSQL setup](documentation/database/postgresql-setup.md)
- [Alembic migrations](documentation/database/alembic-migrations.md)
- [SQLite migration safety](documentation/database/sqlite-to-postgresql.md)
- [Authentication identity](documentation/security/authentication-identity.md)
- [Analysis ownership](documentation/security/analysis-ownership.md)
- [Protected media](documentation/security/protected-media.md)
- [Guest sessions](documentation/security/guest-sessions.md)

## Current architecture

| Area | Current implementation |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Vitest |
| Backend | FastAPI, SQLAlchemy, PostgreSQL/SQLite, Alembic, lazy PyTorch/InsightFace loading, pytest |
| Authentication | Local JWT accounts, Google Identity Services, and disabled-by-default Firebase Admin verification |
| Extension | Manifest V3 plain JavaScript with validation, tests, and a build directory |
| CI | Backend, frontend, extension, and repository-validation GitHub Actions |

## Quick start

Prerequisites are Python 3.11, Node.js 24, npm, Git, PowerShell 7, and Docker Desktop for recommended PostgreSQL development.

```powershell
# Install dependencies and create missing local environment files safely.
.\scripts\setup-development.ps1

# Confirm tools, files, model directory, storage, database configuration, and ports.
.\scripts\verify-environment.ps1

# Explicitly start PostgreSQL and apply Alembic migrations.
.\scripts\start-database.ps1
.\scripts\migrate-database.ps1

# Optional: verify safe, code-defined development reference data.
.\.venv\Scripts\python.exe backend\scripts\seed_development.py

# Start backend and frontend together, wait for health, and open the browser.
python run_web.py

# Confirm actual API health; a started process is not automatically healthy.
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

`python run_web.py` binds both web servers to `127.0.0.1`, opens the frontend automatically, and stops both services with Ctrl+C. Use `python run_web.py --no-browser` when a browser should not open. It performs readiness checks but deliberately does not migrate, seed, or reset the database.

For asynchronous video analysis, start Redis with `.\scripts\start-redis.ps1`, then use `python run_web.py --with-worker`. The same Redis/backend/worker/frontend stack is available through `.\scripts\start-all.ps1` or Docker Compose. See `documentation/video/video-jobs.md` for the owner-scoped API and configured limits.

Run services individually with `scripts/start-backend.ps1`, `scripts/start-frontend.ps1`, and `scripts/start-extension.ps1`. The older `start-all.ps1`/`stop-all.ps1` pair remains available for detached PowerShell startup.

The frontend is at `http://127.0.0.1:5173`, the API is at `http://127.0.0.1:8000`, and API documentation is at `http://127.0.0.1:8000/docs`.

## Safe administrator creation

There is no automatic or default administrator. After explicit schema initialization, create a local administrator interactively:

```powershell
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com
```

The password is entered twice without echo, must pass strength validation, and is never printed. Existing users are refused unless `--update-existing` is deliberately supplied. This command creates only a local account; it does not create a Firebase Authentication user.

## Lifecycle commands are deliberately separate

| Operation | Effect |
| --- | --- |
| Application import/startup | Registers routes, configures lifecycle logging, and serves requests; it does not mutate the database or load models |
| `init_database.py` / `migrate-database.ps1` | Explicitly upgrades schema through Alembic |
| `seed_development.py` | Development-only, idempotent reference-data check; creates no users, histories, analyses, payments, or metrics |
| `create_admin.py` | Interactively creates or explicitly updates one local administrator |

## Tests and quality gates

```powershell
.\scripts\run-tests.ps1
```

This runs backend compilation/pytest, frontend lint/type checking/Vitest/build, and extension syntax checks/tests/build. Individual commands are documented in [testing-strategy.md](documentation/testing-strategy.md).

## Health endpoints

`GET /api/v1/health` reports the safe summary. Dedicated database, model, storage, worker, Redis, payment, and Firebase checks are under `/api/v1/health/*`. Lazy models report `not_loaded`; disabled external integrations report `not_configured`. Health responses never return URLs containing credentials, secrets, tokens, or private paths.

## Current limitations

- Firebase Admin and Stripe test-mode paths are implemented but disabled until valid external credentials, webhook secrets, and price IDs are configured.
- Video analysis uses Redis/Celery when configured. Development alone can use the explicitly labelled single-worker background fallback; staging and production cannot.
- Extension video capture remains subject to browser cross-origin, DRM, and content-script restrictions.
- Production still requires external secret management, HTTPS/reverse-proxy validation, object storage, backup exercises, Redis/PostgreSQL load testing, and a security review.
- Model training, dataset development, and DeepSightNet changes remain outside this repository phase.

Current Alembic head is `0006_external_identity_billing`. Apply it explicitly with `.\scripts\migrate-database.ps1`; application startup never migrates automatically.
