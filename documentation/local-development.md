# Local Development

## Prerequisites

- Windows PowerShell 7 (`pwsh`)
- Python 3.11 via the Windows Python launcher
- Node.js 24 and npm
- Git
- Optional CUDA support; CPU fallback is selected when CUDA is unavailable

## Setup

From the repository root:

```powershell
.\scripts\setup-development.ps1
.\scripts\verify-environment.ps1
.\scripts\start-database.ps1
.\scripts\migrate-database.ps1
```

Setup creates `.venv`, installs runtime/development Python dependencies, installs frontend and extension packages, copies missing environment examples, and creates local runtime directories. It never overwrites an existing `.env`, initializes the database, or creates users.

Review `backend/.env` and `frontend/.env` after setup. Use a randomly generated local `SECRET_KEY` of at least 32 characters. Set `FIREBASE_ENABLED=false` unless optional Firestore mirroring is deliberately configured. Do not commit either environment file.

## Start and stop

The simplest development command starts both web services, verifies readiness, and opens the frontend:

```powershell
python run_web.py
```

Both services bind only to `127.0.0.1`. Press Ctrl+C in the launcher terminal to stop both process trees. Optional flags include `--no-browser`, `--no-reload`, `--backend-port`, and `--frontend-port`. The launcher never runs Alembic, seeding, administrator creation, or database reset automatically.

Run services in foreground terminals:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

Or open both as recorded background development processes:

```powershell
.\scripts\start-all.ps1
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
.\scripts\stop-all.ps1
```

`start-all.ps1` records only the processes it created under ignored `.run/` state. `stop-all.ps1` validates process identity and start time before stopping anything.

Build the extension and print load-unpacked instructions:

```powershell
.\scripts\start-extension.ps1
```

Load `extension/dist` at `chrome://extensions`. Change `extension/config.js` and rebuild when the backend URL differs from the local default.

## Explicit data operations

```powershell
# Schema only, migration-controlled
.\scripts\migrate-database.ps1

# Safe development reference configuration only
.\.venv\Scripts\python.exe backend\scripts\seed_development.py

# One interactive local administrator
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com
```

These operations are intentionally absent from application import and startup.

## Troubleshooting

- If environment verification reports occupied ports, stop the existing service or choose another port manually.
- If database health is `unavailable`, run `scripts/check_database.py`, verify PostgreSQL readiness, and apply migrations. For SQLite, verify its parent directory is writable.
- `not_loaded` is healthy for lazy models before first inference. `disabled` is expected in tests.
- A missing checkpoint produces a controlled inference error; setup never downloads or modifies model weights.
