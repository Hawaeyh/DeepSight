[CmdletBinding()]
param([string]$Revision = "head")

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) { throw "Virtual environment missing." }

Push-Location "$RepoRoot\backend"
try {
    & $PythonPath scripts/check_database.py
    if ($LASTEXITCODE -ne 0) { throw "Database readiness check failed." }
    & $PythonPath -m alembic -c alembic.ini upgrade $Revision
    if ($LASTEXITCODE -ne 0) { throw "Alembic upgrade failed." }
    & $PythonPath -m alembic -c alembic.ini current
}
finally { Pop-Location }
