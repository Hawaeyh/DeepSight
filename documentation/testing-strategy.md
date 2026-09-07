# Testing Strategy

## Test isolation

Backend tests set their environment before importing application modules. They use a unique temporary SQLite database and temporary storage/report directories, disable Firebase, and disable model loading. They never reference the developer database, credentials, deployed checkpoints, cloud storage, email, or Stripe.

Database tests migrate fresh temporary SQLite files and verify head revision, downgrade/re-upgrade, model drift, indexes, unique constraints, foreign keys, cascades, and the transfer dry run. CI also provides a dedicated ephemeral PostgreSQL 17 service through `POSTGRES_TEST_DATABASE_URL`; PostgreSQL tests skip explicitly when that isolated URL is absent locally.

Baseline backend coverage verifies:

- `app.main` imports successfully.
- Import creates neither SQLite files nor storage directories.
- Import creates no administrator and does not reset an existing password or role.
- Configuration rejects blank database URLs and short secrets.
- Schema initialization works only through the explicit function/command.
- The health endpoint returns database/model state without secrets.

Frontend Vitest/jsdom coverage verifies the public route, unknown-route redirect, API URL fallback/configuration, and authentication-provider loading state. Extension Node tests verify Manifest V3, required popup/content/background entries, source existence, configurable API use, and basic embedded-secret patterns.

## Run everything

```powershell
.\scripts\run-tests.ps1
```

The script exits non-zero if any required stage fails.

## Run individual suites

```powershell
# Backend
Set-Location backend
& ..\.venv\Scripts\python.exe -m compileall -q app scripts tests
& ..\.venv\Scripts\python.exe -m pytest -q

# Frontend
Set-Location frontend
npm run lint
npm run typecheck
npm test
npm run build

# Extension
Set-Location extension
npm run lint
npm run typecheck
npm test
npm run build
```

## Continuous integration

- `backend-tests.yml`: Python 3.11, PostgreSQL 17 service, Alembic upgrade/readiness, compilation, SQLite tests, PostgreSQL integration tests, and drift checks.
- `frontend-checks.yml`: npm clean install, lint, type checking, Vitest, production build.
- `extension-checks.yml`: clean install, syntax/type validation, tests, package build.
- `repository-validation.yml`: required examples, forbidden tracked secrets/weights, whitespace, and local Markdown links.

Deployment is intentionally absent from these workflows.
