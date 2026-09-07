# DeepSight Current System Audit

Audit date: 2026-07-27  
Scope: Phase 1 repository, application, configuration, deployment, and security audit. Model training, datasets, model evaluation, and DeepSightNet improvement were not modified.

## 1. Executive summary

DeepSight is a working prototype rather than a production-ready platform. The React application builds, the FastAPI application imports, and image and synchronous video inference paths exist. The repository also contains a loadable Chrome Manifest V3 extension for webpage image scanning.

The highest-priority blocker is missing data ownership. `Analysis` has no user or guest owner, and analysis history, individual results, deletes, verification, feedback, reports, dashboard data, Firestore mirrors, and media URLs are not scoped to a caller. A second critical issue is import-time creation and resetting of a known administrator account. Real user media must not be processed in an internet-accessible deployment until these issues are resolved.

## 2. Repository inventory

| Path | Current purpose | Audit notes |
| --- | --- | --- |
| `frontend/` | React/TypeScript web application | Active application; `frontend/README.md` is still the Vite template |
| `backend/` | FastAPI API, SQLAlchemy models, inference, uploads, reports | Active application; `backend/README.md` is empty |
| `extension/` | Chrome extension | Runnable files are at the extension root; parallel `src/` folders are empty |
| `docs/` | Two deployment/pipeline notes | Does not match the requested `documentation/` structure |
| `documentation/` | Phase 1 audit and roadmap | Created during this phase |
| `ai/` | Intended model-lab structure | Empty and duplicated conceptually by `backend/app/ai/` |
| `models/` | Intended model storage structure | Empty; deployed weights are instead under `backend/app/models/production/` |
| `datasets/` | Hard-example dataset output | Contains runtime/user-derived data and is ignored |
| `scripts/` | Intended automation | Empty; no setup/start/test PowerShell scripts exist |
| `tests/`, `backend/tests/` | Intended tests | Empty; no executable test suite exists |
| `.github/workflows/` | Intended CI | Empty; no CI workflows exist |

Important root files include `README.md`, `.gitignore`, `.firebaserc.example`, `firebase.json`, `env.cloudrun.yaml`, and `ML7-VIDS-DeepSight-System.code-workspace`. The license and workspace files are empty.

## 3. Current application structure

### Frontend

- Vite entry points: `frontend/src/main.tsx` and `frontend/src/App.tsx`.
- Routing: `frontend/src/router/AppRouter.tsx`.
- Shared UI and layout: `frontend/src/components/` and `frontend/src/layouts/`.
- Image and history features have partial feature-folder organization under `frontend/src/features/`.
- Video, webcam/live, authentication, plans, settings, reports, extension information, and admin pages remain directly under `frontend/src/pages/`.
- The API client stores a bearer token and guest UUID in `localStorage` and targets `VITE_API_URL`.

Current public routes are `/`, `/login`, `/register`, `/image`, and `/plans`. Authenticated routes are `/dashboard`, `/video`, `/history`, `/reports`, `/settings`, and `/profile`. Plan-gated routes are `/extension` and `/live`. Admin routes are `/admin`, `/admin/model-reports`, and `/admin/users`.

### Backend

- Entry point: `backend/app/main.py`, normally launched by `backend/run.py`.
- API modules: authentication, image analysis, video analysis, history, reports, feedback, subscriptions, dashboard, admin, model listing, Firebase status/sync, and health.
- Persistence: SQLAlchemy with the active base/session in `backend/app/core/database.py`.
- Inference: `backend/app/ai/`; weights are under `backend/app/models/production/`.
- Runtime files: `backend/uploads/`, `backend/reports/`, and the SQLite database.
- Firestore is an optional secondary mirror, not the source of authenticated ownership.

### Extension

- `manifest.json` correctly declares Manifest V3.
- `popup.js` performs local account login and page-scan commands.
- `service-worker.js` downloads an image URL and posts it to `/api/v1/analysis/image`.
- `content-script.js` scans up to 16 sufficiently large images and adds fixed-position result labels.
- The extension has hard-coded local API URLs and broad `<all_urls>` host access.
- `extension/package.json`, `extension/vite.config.ts`, and the entire `extension/src/` tree are empty placeholders. This creates two competing intended structures.

### Database and deployment

- The working database is SQLite (`ml7_deepsight.db`), not PostgreSQL.
- SQLAlchemy calls `Base.metadata.create_all()` at import time; Alembic is installed but no Alembic directory or migrations exist.
- A backend Dockerfile and Firebase Hosting configuration exist as uncommitted work.
- Docker Compose, Redis, Celery/background workers, frontend container definition, monitoring, backups, and rollback automation are absent.
- `backend/requirements.txt` is UTF-16 LE. The Dockerfile converts it to UTF-8 during build, but ordinary tooling may not parse it consistently.

## 4. Feature implementation status

| Capability | Status | Findings |
| --- | --- | --- |
| Image analysis | Prototype works | Upload, model selection, inference, result persistence, and feedback UI exist; server validation and ownership are insufficient |
| Video analysis | Partial, synchronous | Upload and one-frame-per-second inference exist; request blocks until completion and lacks tracking, progress, cancellation, face tracking, quality filtering, bounded sampling, and suspicious segments |
| Webcam/live | UI prototype | Browser captures a JPEG every four seconds and calls the image endpoint; no dedicated webcam API, no no-face skip, rolling aggregation, stability rules, or session history |
| History | Functional but unsafe | List/detail/delete/verify operate on the global analysis table without authentication or ownership |
| Authentication | Partial local implementation | Local password JWT and Google Identity Services exist; Firebase client authentication, Firebase token verification, email verification, reset flow, secure cookies, refresh/revocation, and rate limiting are absent |
| Guest sessions | Unsafe prototype | Client creates `X-Guest-ID` in local storage; no server-issued, hashed, expiring, HttpOnly guest session and anonymous callers can share the `guest:anonymous` quota identity |
| Admin | Partial | Role-protected user and usage endpoints plus dashboard pages exist; model registry lifecycle, audit logs, production monitoring, and comprehensive performance pages are absent |
| Subscription | In-memory plan rules only | Entitlement and usage tables exist; plans are constants, quotas are non-atomic, and Stripe checkout/webhooks/customer portal are absent |
| Reports | Prototype works but unsafe | PDFs can be generated by numeric analysis ID without authentication or ownership |
| Notifications | Missing | No notification model, service, endpoint, or UI workflow was found |
| Browser extension images | Prototype | Manual and continuous image scans exist; remote-image fetch/CORS restrictions, broad permissions, token storage, throttling, and stale labels remain concerns |
| Browser extension video | Missing | No video element discovery, frame capture, video message type, rolling buffer, stable overlay, or restricted-page handling exists |
| Tests and CI | Missing | Test directories and workflow directory are empty; `backend/test_model.py` is a manual loader for a nonexistent `current_model.pth`, not a test |

## 5. Duplicated, obsolete, misplaced, or broken items

- `backend/app/core/database.py` is the active database module; `backend/app/database/database.py`, `session.py`, `base.py`, and `init_db.py` form a second, partly empty SQLite setup and appear obsolete.
- `frontend/src/pages/HistoryPage.tsx` overlaps the active feature implementation at `frontend/src/features/history/pages/HistoryPage.tsx`.
- History types and image metadata types also exist in both top-level and feature folders.
- `extension/src/` describes a future modular layout, while all runnable code is at the extension root; the package and Vite files are empty.
- Root `ai/`, `models/`, `scripts/`, and `tests/` are placeholders. Active inference and model weights are nested in the backend.
- `backend/app/requirements.txt`, two backend READMEs, the license, and several source placeholders are empty.
- Python bytecode and runtime uploads exist locally. They are ignored but should be cleaned through an explicit, recoverable operation in a later phase.
- Deployed `.pth` weights are stored inside application source rather than a controlled model registry/release location.
- `backend/test_model.py` points to `current_model.pth`, which is not present.
- The frontend history and API shapes contain overlapping definitions that may drift.
- Several rendered strings contain mojibake such as `Â·`, indicating an encoding problem.

No files were moved or deleted during Phase 1.

## 6. Security findings

### Critical

1. `Analysis` has no `owner_user_id`, Firebase UID, or guest-session owner.
2. `/analysis/history`, `/analysis/{id}`, `/history`, `/history/{id}`, deletes, verification, feedback, and report downloads accept global numeric IDs without caller ownership checks.
3. Dashboard endpoints return system-wide analysis information without authentication; authenticated user pages therefore expose global data.
4. `/media` exposes all uploaded images, videos, and extracted frames through guessable/static paths with no authorization.
5. `backend/app/main.py` creates or resets two admin accounts on every import with the known password `admin1234`.

### High

- Browser tokens are stored in `localStorage` and `chrome.storage.local`, increasing the impact of XSS or extension compromise.
- Any Chrome extension origin is allowed by the backend CORS regex; extension identity is not allowlisted.
- The client-provided guest UUID is trusted as quota identity and is easily reset or forged; no IP/session rate limiter exists.
- Upload handling trusts filename extensions, streams directly to disk, and does not enforce MIME signatures, maximum bytes, decompression limits, video duration, or codec checks.
- Feedback can copy an arbitrary analysis file into hard-example datasets without authentication or ownership.
- Firestore documents are keyed by global numeric analysis ID and contain no owner identifier.
- Google-created users store the sentinel text `google-oauth` in the password column instead of representing authentication providers explicitly.

### Medium

- Quota checks and usage inserts are separate operations and can race.
- SQLite tables are created at import time without versioned migrations.
- Generated media and reports have no retention cleanup.
- Error handling is local and inconsistent; there is no global exception envelope or request ID.
- Logging configuration is empty, while inference initialization prints environment/model details during import.
- The repository has no automated dependency, secret, or security scans.

## 7. Why video detection is unreliable

The current web video path runs completely inside one HTTP request. It decodes every frame and saves one frame at roughly each second, with no maximum duration or sample cap. Long or malformed videos can monopolize CPU/GPU, disk, and the request worker, while the frontend waits up to ten minutes.

Every saved full frame is resized directly to 224×224 and classified. There is no face detection/cropping, face tracking, blur/occlusion/exposure filtering, scene-aware sampling, batching, temporal smoothing, or retry/fallback codec handling. Timestamps are inferred as `index * 1.0` rather than retained from the decoder. The final label is a hard majority of per-frame classes and its reported confidence is vote agreement, while real/fake probabilities are independent averages; these values can disagree. A tie is always labeled Real. Extracted frames remain publicly accessible and are not cleaned up.

The API does not create a queued job, progress record, cancellation signal, event stream, suspicious segment model, or failed-job state. This explains stalled requests and makes the feature unsuitable for reliable production workloads even when short local videos complete.

## 8. Why extension video detection does not work

Extension video detection is not implemented. The manifest and content script scan `document.images` only. The service worker accepts only `ANALYZE_IMAGE`, and the popup offers only a page image scan. There is no `<video>` enumeration, canvas capture, frame schedule, rolling prediction window, stable overlay, pause/cleanup lifecycle, or API contract for extension video frames.

Even after implementation, protected streams, DRM, cross-origin video canvases, blob URLs, sandboxed frames, browser-internal pages, and content-security restrictions will require explicit unsupported-state handling. The current service worker also downloads remote images itself; remote servers may reject extension-origin requests or require authentication that `credentials: "omit"` deliberately excludes.

## 9. Environment variable audit

Variables currently consumed by code are:

- Backend: `APP_NAME`, `APP_VERSION`, `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `FIREBASE_CREDENTIALS_PATH`, `FIREBASE_PROJECT_ID`, `FIREBASE_COLLECTION`, `GOOGLE_CLIENT_ID`, `FRONTEND_ORIGINS`.
- Frontend: `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`.
- Backend container: `PORT`.

Variables required by the target architecture but not wired into code are `APP_ENV`, `FRONTEND_URL`, `BACKEND_URL`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `MODEL_ROOT`, `STORAGE_BACKEND`, `LOCAL_STORAGE_ROOT`, `REDIS_URL`, `JWT_COOKIE_SECURE`, and `COOKIE_DOMAIN`. The target outline names `VITE_API_BASE_URL` and Firebase/Stripe frontend variables, whereas current code uses `VITE_API_URL` and Google Identity Services only. This naming must be migrated deliberately rather than silently changed.

The root `env.cloudrun.yaml` is an environment-specific file and was not ignored before this audit. It does not currently show a database URL or secret key, so a deployment using only it cannot satisfy required backend settings unless they are injected separately.

## 10. Current local-development commands

Backend, from the repository root:

```powershell
Copy-Item .env.example backend/.env
py -3.11 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Set-Location backend
python run.py
```

Frontend, in a second terminal:

```powershell
Copy-Item frontend/.env.example frontend/.env
Set-Location frontend
npm install
npm run dev
```

Extension: load the `extension/` directory unpacked through `chrome://extensions`. There are currently no database, Redis, worker, all-in-one, or Docker Compose start commands.

## 11. Validation performed and errors encountered

- `npm run build`: passed. Vite warned that the main JavaScript chunk is about 882 kB (about 254 kB gzip), above its 500 kB warning threshold.
- `npm run lint`: completed with two Fast Refresh warnings in `AuthContext.tsx` and `DashboardContext.tsx`.
- `python -m compileall -q app`: passed using Python 3.11.9.
- `import app.main`: passed and initialized CUDA/InsightFace. This import also has application side effects: table creation and administrator seeding.
- `python -m pytest -q`: failed because `pytest` is not installed in the current virtual environment. No test files were found in the repository audit.
- No end-to-end inference was executed because that would create analysis/media records and was not required for the read-only audit.
- Docker and cloud deployment were not executed; their credentials and target services are outside this audit.

## 12. Phase 1 changes

Only the following approved paths were changed or created:

- `.gitignore`
- `.env.example`
- `README.md`
- `documentation/current-system-audit.md`
- `documentation/development-roadmap.md`

Pre-existing uncommitted backend, frontend, Firebase, and deployment work was preserved.
