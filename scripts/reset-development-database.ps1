[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$validation = & $PythonPath -c "import sys;sys.path.insert(0,'backend');from app.core.config import settings;from sqlalchemy.engine import make_url;u=make_url(settings.DATABASE_URL);ok=settings.APP_ENV=='development' and u.drivername=='postgresql+psycopg' and u.host in {'localhost','127.0.0.1'} and u.database=='deepsight';print('SAFE' if ok else 'REFUSE')"
if ($validation -ne "SAFE") {
    throw "Reset is restricted to APP_ENV=development and local PostgreSQL database 'deepsight'."
}

Write-Warning "This deletes every table and row in the local PostgreSQL 'deepsight' public schema."
$confirmation = Read-Host "Type RESET DEEPSIGHT DEVELOPMENT DATABASE to continue"
if ($confirmation -ne "RESET DEEPSIGHT DEVELOPMENT DATABASE") { throw "Reset cancelled." }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker is unavailable." }

Push-Location $RepoRoot
try {
    docker compose exec -T postgres psql -U deepsight -d deepsight -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL schema reset failed." }
}
finally { Pop-Location }

& "$PSScriptRoot\migrate-database.ps1"
& $PythonPath "$RepoRoot\backend\scripts\seed_development.py"
Write-Host "Development schema recreated. No administrator was created."
