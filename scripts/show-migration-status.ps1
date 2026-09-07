[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
Push-Location "$RepoRoot\backend"
try {
    Write-Host "Current revision:"
    & $PythonPath -m alembic -c alembic.ini current
    Write-Host "Head revision:"
    & $PythonPath -m alembic -c alembic.ini heads
    Write-Host "Migration history:"
    & $PythonPath -m alembic -c alembic.ini history --verbose
}
finally { Pop-Location }
