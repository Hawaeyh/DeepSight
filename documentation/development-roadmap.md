# DeepSight Development Roadmap

This roadmap migrates the current prototype safely toward the target DeepSight platform. Each phase should ship with migrations, tests, documentation, and a rollback path. Model training and DeepSightNet changes remain in the separate Model Lab project.

## Migration principles

- Preserve the current runnable paths until their replacements pass compatibility tests.
- Add versioned database migrations before changing persisted models.
- Establish ownership and protected storage before expanding features or accepting real user data.
- Use adapters for authentication, storage, inference, payments, and jobs so local development remains usable.
- Do not move or delete duplicate/placeholder files until imports and references prove they are unused.
- Never migrate production data through ad hoc scripts; use reviewed, idempotent migrations with backups.

## Phase 1 — Audit and foundation

Status: foundation stabilization completed with explicit schema/admin commands, lazy inference imports, baseline tests, local scripts, and CI. Ownership remains deliberately deferred.

1. Preserve the current dirty worktree and agree on a baseline commit.
2. Resolve encoding issues, especially the UTF-16 requirements file and mojibake strings.
3. Add structured logging, request IDs, global error handling, and environment validation.
4. Add PowerShell startup/test scripts and Docker Compose for PostgreSQL and Redis only after their consumers exist.
5. Add backend, frontend, and extension test harnesses plus baseline CI.
6. Decide which duplicate structures are canonical, then deprecate old paths without deleting them prematurely.

Exit criteria: clean reproducible setup on a new machine, documented configuration, health check, baseline tests, and no import-time account creation.

## Phase 2 — Database foundation

1. Introduce PostgreSQL configuration while retaining a disposable SQLite option for limited tests if useful.
2. Create an Alembic environment and baseline migration matching current tables.
3. Add normalized plan, entitlement, usage, model registry, guest session, job, audit, and notification tables.
4. Add indexes, constraints, timezone-aware timestamps, and database health checks.
5. Seed only non-secret plan configuration; never seed known credentials.

Exit criteria: upgrade/downgrade tested against a database backup, no `create_all()` in application startup, and a documented schema.

## Phase 3 — Authentication

1. Choose Firebase Authentication as the external identity source and store Firebase UID on the local user.
2. Verify Firebase ID tokens in FastAPI and synchronize a local profile on first access.
3. Implement email/password, Google sign-in, email verification, password reset, suspended account, and account deletion flows.
4. Replace long-lived browser storage where practical with short-lived tokens or secure server-managed cookies; document extension token constraints.
5. Add login throttling, revocation/session-expiry behavior, and role tests.

Exit criteria: all protected APIs use one verified identity dependency and forged/expired/revoked token tests pass.

## Phase 4 — Ownership and privacy (release blocker)

1. Add nullable `owner_user_id` and `guest_session_id` to analyses through a migration, backfill legacy rows as explicitly unowned, and require exactly one valid ownership mode for new rows.
2. Create cryptographically random, hashed, expiring guest sessions delivered through an HttpOnly cookie; rate-limit by session and privacy-preserving IP hash.
3. Scope every history, detail, update, delete, feedback, dashboard, report, and Firestore operation to the verified owner. Admin access must be explicit and audited.
4. Replace the public media mount with authorized download endpoints or short-lived signed URLs.
5. Add retention jobs and safe deletion of source media, frames, reports, and Firestore mirrors.
6. Add cross-user, guest, ID-enumeration, download, delete, feedback, and admin-boundary tests.

Exit criteria: two users and two guests cannot observe or mutate one another's records or media; all denial paths are tested.

## Phase 5 — Image analysis

1. Validate extension, MIME type, magic bytes, decoded dimensions, pixel count, and streaming byte limits before persistence.
2. Isolate untrusted decoding and delete failed uploads.
3. Standardize model identifiers and response semantics.
4. Persist ownership, provenance, model version, calibrated scores, and processing status transactionally.
5. Complete one-screen analysis UX, accessible errors, feedback, and owner-protected reports.

Exit criteria: validation, inference, failure cleanup, ownership, feedback, and reports have API and UI tests.

## Phase 6 — Video analysis

1. Add Redis plus a worker and create durable queued/running/completed/failed/cancelled job states.
2. Stream uploads with size, duration, container, codec, and decode validation.
3. Implement bounded representative sampling, scene changes, accurate timestamps, face detection/tracking, and frame-quality filtering.
4. Batch inference and aggregate calibrated track/frame scores using a documented policy; do not use simple vote agreement as confidence.
5. Store only necessary thumbnails with retention controls.
6. Add progress polling or server-sent events, cancellation, suspicious segments, and owner-protected reports.
7. Test short/long, variable-frame-rate, no-face, corrupted, rotated, multi-face, cancelled, and worker-retry cases.

Exit criteria: API workers remain responsive during long videos; jobs are resumable/observable, bounded, cancelable, owner-scoped, and reproducible.

## Phase 7 — Webcam analysis

1. Add a dedicated ephemeral webcam endpoint or session protocol.
2. Handle permissions, device changes, track termination, tab visibility, and cleanup.
3. Sample at a controlled rate, skip no-face/low-quality frames, and use a bounded rolling buffer.
4. Apply hysteresis/minimum-evidence rules so labels do not flicker.
5. Persist only opted-in session summaries, never raw frames by default.

Exit criteria: stable results, explicit privacy behavior, graceful camera errors, and session tests.

## Phase 8 — Browser extension

1. Select either the root no-build implementation or the modular TypeScript/Vite structure, then migrate with parity tests.
2. Restrict host permissions using optional permissions where possible and allowlist the production extension origin in CORS.
3. Centralize environment-specific API configuration and implement secure authentication renewal/logout.
4. Add bounded concurrent image scanning, URL/result caching, responsive label positioning, mutation debouncing, and cleanup.
5. Implement visible video discovery and controlled canvas sampling only where browser security permits.
6. Add rolling video aggregation and a single stable overlay; report DRM, tainted canvas, cross-origin, sandbox, and restricted pages as unsupported rather than failing silently.
7. Save extension history through owner-scoped APIs and add unit/integration tests.

Exit criteria: packaged MV3 build passes Chrome review-oriented permission/privacy checks and behaves predictably on supported and unsupported media.

## Phase 9 — Admin dashboard

1. Separate user analytics from admin system-wide metrics.
2. Add model registry records, immutable model artifacts, validation state, activation, rollback, and audit events.
3. Import offline metrics from approved Model Lab artifacts without coupling this repository to training code.
4. Add production drift/feedback metrics, video job health, extension telemetry with consent, and system-health views.
5. Protect every route server-side and test privilege escalation.

Exit criteria: all sensitive changes are authorized, audited, reversible, and covered by admin authorization tests.

## Phase 10 — Subscriptions and payments

1. Move plan definitions and entitlements into the database.
2. Implement atomic usage reservations with commit/release semantics for long jobs.
3. Add Stripe Checkout, signed idempotent webhooks, customer portal, cancellation, and entitlement reconciliation.
4. Never trust client-supplied plans or JWT role claims without a current database lookup.

Exit criteria: webhook replay, race, cancellation, failed-payment, refund, and quota concurrency tests pass in Stripe test mode.

## Phase 11 — Documentation and CI

1. Complete root/component READMEs, architecture, setup, API, security, database, deployment, testing, and user guides.
2. Add issue and pull-request templates.
3. Add formatting, lint, type, unit, integration, build, dependency, secret, container, and security workflows.
4. Store no datasets, user media, secrets, or uncontrolled weights in Git.

Exit criteria: pull requests cannot merge when required checks fail and a new contributor can reproduce local development from documentation.

## Phase 12 — Staging readiness

1. Create isolated development, staging, and production projects and credentials.
2. Build immutable frontend/backend/worker images with health/readiness checks.
3. Add managed PostgreSQL/Redis, private storage, backups, restore drills, monitoring, alerting, and retention.
4. Document deployment, rollback, incident response, and secret rotation.
5. Run a complete staging smoke, security, privacy, load, and recovery test.

Exit criteria: signed-off staging evidence, successful restore/rollback drill, no critical/high security findings, and explicit production approval.

## Recommended next step

The PostgreSQL/Alembic foundation is implemented. Next: authentication identity integration and analysis ownership. Begin only after PostgreSQL works in the target local environment, Alembic upgrades and migration tests pass, and the legacy-data migration procedure has been rehearsed on copies. Production exposure remains blocked until ownership and protected media access are complete.
