[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Revision,
    [switch]$ConfirmProduction
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$AppEnvironment = & $PythonPath -c "import sys;sys.path.insert(0,'backend');from app.core.config import settings;print(settings.APP_ENV)"
if ($AppEnvironment -eq "production" -and -not $ConfirmProduction) {
    throw "Production downgrade requires -ConfirmProduction."
}

Push-Location "$RepoRoot\backend"
try {
    & $PythonPath -m alembic -c alembic.ini downgrade $Revision
    if ($LASTEXITCODE -ne 0) { throw "Alembic downgrade failed." }
    & $PythonPath -m alembic -c alembic.ini current
}
finally { Pop-Location }
