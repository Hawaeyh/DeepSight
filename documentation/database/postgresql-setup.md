# PostgreSQL setup

Prerequisites are Python 3.11, Docker Desktop with Compose, Node.js, and the repository virtual environment.

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
.\scripts\start-database.ps1
.\scripts\migrate-database.ps1
.\.venv\Scripts\python.exe backend\scripts\seed_development.py
.\.venv\Scripts\python.exe backend\scripts\create_admin.py --email admin@example.com
.\scripts\start-backend.ps1
```

The Compose credentials are development-only and may be overridden with environment variables. Never use them in production. Startup order is health-gated, but the application readiness check still fails safely if PostgreSQL becomes unavailable. Database URLs and passwords are not printed.

For SQLite-only use, set `DATABASE_URL=sqlite:///./deepsight.db`. Its concurrency, typing, collation, and migration behavior differ from PostgreSQL; it is not the deployment recommendation.
