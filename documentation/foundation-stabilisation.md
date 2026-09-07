# Foundation Stabilisation

## Scope completed

- Removed table creation and known administrator creation/password resetting from application import.
- Removed email-specific entitlement mutation.
- Added explicit schema initialization, safe development seed, and interactive administrator commands.
- Made filesystem paths declarative; runtime directories and PDF directories are created only by explicit setup or the operation that writes them.
- Deferred image/video inference imports, checkpoint loads, and InsightFace initialization until inference requests.
- Added safe model state reporting and disabled external/model behavior for tests.
- Added formatted startup/shutdown/request logging with request IDs.
- Normalized `backend/requirements.txt` from UTF-16 LE to UTF-8 without BOM and declared previously implicit inference packages.
- Added development dependencies and isolated backend tests.
- Added Vitest/jsdom frontend tests and removed both Fast Refresh warnings by separating context definitions/hooks from providers.
- Added lazy route imports. The largest initial frontend chunk changed from approximately 882.21 kB (253.86 kB gzip) to 293.60 kB (96.19 kB gzip). A separate chart chunk remains approximately 366.04 kB (105.11 kB gzip).
- Added extension syntax checks, MV3 validation, tests, configurable API URL, and deterministic `dist` build.
- Added local PowerShell setup, verification, start, stop, and aggregate test scripts.
- Added baseline GitHub Actions without deployment.

## Dependency warnings

The compatible PostCSS advisory was resolved with non-forced `npm audit fix`. npm still reports two high-severity findings for `react-router` and `react-router-dom`; its proposed remediation force-installs `react-router-dom@7.11.0` outside the declared range and labels the change breaking. That forced downgrade was not applied. The current application does not use React Router's server-component action mode referenced by the advisory, but dependency remediation remains open and should be retested when an upstream compatible release is available.

The local Python repair left a pip warning about an old `~ympy` backup directory even though `sympy 1.14.0` imports successfully. The ignored virtual environment can be recreated with `setup-development.ps1` if a clean local package directory is required.

## Import guarantees

Automated subprocess tests verify that importing `app.main` against a nonexistent temporary SQLite path creates neither the database nor storage directory. A second test creates one ordinary user explicitly, imports `app.main`, and verifies the user count, password hash, and role remain unchanged.

## Intentionally deferred

This phase does not implement PostgreSQL, Alembic, ownership, protected media, Redis/Celery, asynchronous video, Stripe, extension video, model training, or major UI redesign.

## Remaining security boundary

The stable foundation is still not safe for production user data. Analysis ownership, history authorization, report authorization, and private media delivery remain unresolved critical findings. Existing local JWT/Firebase architecture also requires its dedicated authentication phase.

## Next phase

The next recommended and authorized phase is PostgreSQL and Alembic foundation work, provided all stabilization quality gates continue to pass.
