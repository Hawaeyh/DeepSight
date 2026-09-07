[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) { throw "Virtual environment missing. Run scripts/setup-development.ps1." }
if (-not (Test-Path "$RepoRoot\backend\.env")) { throw "backend/.env is missing." }

Push-Location "$RepoRoot\backend"
try {
    & $PythonPath scripts/check_database.py --require-head
    if ($LASTEXITCODE -ne 0) { throw "Database is unavailable. Start it and run migrations first." }
    & $PythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
finally { Pop-Location }
