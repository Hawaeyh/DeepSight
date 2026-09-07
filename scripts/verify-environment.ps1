[CmdletBinding()]
param(
    [switch]$RequireAvailablePorts
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Failures = [System.Collections.Generic.List[string]]::new()
$Warnings = [System.Collections.Generic.List[string]]::new()

function Add-Check {
    param([string]$Name, [bool]$Passed, [string]$FailureMessage)
    if ($Passed) { Write-Host "[OK] $Name" -ForegroundColor Green }
    else { Write-Host "[FAIL] $Name" -ForegroundColor Red; $Failures.Add($FailureMessage) }
}

Push-Location $RepoRoot
try {
    $pythonVersion = & py -3.11 --version 2>&1
    Add-Check "Python 3.11" ($LASTEXITCODE -eq 0 -and "$pythonVersion" -match "Python 3\.11\.") "Python 3.11 is required."

    $PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    Add-Check "Virtual environment" (Test-Path -LiteralPath $PythonPath) "Run scripts/setup-development.ps1 to create .venv."
    if (Test-Path -LiteralPath $PythonPath) {
        & $PythonPath -m pip --version *> $null
        Add-Check "Virtual environment pip" ($LASTEXITCODE -eq 0) "pip is unavailable in .venv."
        & $PythonPath -c "import fastapi, sqlalchemy, pydantic_settings" *> $null
        Add-Check "Backend dependencies" ($LASTEXITCODE -eq 0) "Backend dependencies are incomplete."
    }

    & node --version *> $null
    Add-Check "Node.js" ($LASTEXITCODE -eq 0) "Node.js is required."
    & npm --version *> $null
    Add-Check "npm" ($LASTEXITCODE -eq 0) "npm is required."
    Add-Check "Frontend dependencies" (Test-Path "$RepoRoot\frontend\node_modules") "Run npm install in frontend."
    Add-Check "Extension package" (Test-Path "$RepoRoot\extension\package.json") "extension/package.json is missing."

    Add-Check "Backend environment" (Test-Path "$RepoRoot\backend\.env") "Copy backend/.env.example to backend/.env and configure it."
    Add-Check "Frontend environment" (Test-Path "$RepoRoot\frontend\.env") "Copy frontend/.env.example to frontend/.env."
    Add-Check "Model directory" (Test-Path "$RepoRoot\backend\app\models\production") "The deployed model directory is missing."

    $StorageRoot = "$RepoRoot\backend\uploads"
    Add-Check "Writable storage directory" (Test-Path $StorageRoot -PathType Container) "Run setup-development.ps1 to create local storage."
    if (Test-Path $StorageRoot -PathType Container) {
        $probe = Join-Path $StorageRoot ".write-probe-$PID"
        try { [System.IO.File]::WriteAllText($probe, "probe"); Remove-Item -LiteralPath $probe; Write-Host "[OK] Storage is writable" -ForegroundColor Green }
        catch { $Failures.Add("Backend storage is not writable.") }
    }

    if ((Test-Path $PythonPath) -and (Test-Path "$RepoRoot\backend\.env")) {
        & $PythonPath -c "import sys; sys.path.insert(0, 'backend'); from app.core.config import settings; from sqlalchemy.engine import make_url; u=make_url(settings.DATABASE_URL); assert u.get_backend_name() in ('sqlite','postgresql'); print('[OK] Supported database configuration: '+u.get_backend_name()); weak=len(settings.SECRET_KEY)<32; print('[WARN] SECRET_KEY should contain at least 32 characters.' if weak else '[OK] SECRET_KEY length'); raise SystemExit(2 if weak else 0)"
        $configExit = $LASTEXITCODE
        if ($configExit -eq 1) { $Failures.Add("Backend database configuration is invalid or unsupported.") }
        elseif ($configExit -eq 2) { $Warnings.Add("The existing backend SECRET_KEY is accepted for compatibility but should be rotated to 32+ random characters.") }
    }

    foreach ($port in 8000, 5173) {
        $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
        if ($listener -and $RequireAvailablePorts) { $Failures.Add("Port $port is already in use."); Write-Host "[FAIL] Port $port is already in use" -ForegroundColor Red }
        elseif ($listener) { $Warnings.Add("Port $port is already in use."); Write-Host "[WARN] Port $port is already in use" -ForegroundColor Yellow }
        else { Write-Host "[OK] Port $port is available" -ForegroundColor Green }
    }
}
finally { Pop-Location }

foreach ($warning in $Warnings) { Write-Warning $warning }
if ($Failures.Count -gt 0) {
    $Failures | ForEach-Object { Write-Error $_ -ErrorAction Continue }
    exit 1
}
Write-Host "Environment verification passed. Secret values were not displayed." -ForegroundColor Green
exit 0
