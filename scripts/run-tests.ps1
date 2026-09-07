[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Failed = [System.Collections.Generic.List[string]]::new()

function Invoke-Check {
    param([string]$Name, [scriptblock]$Command)
    Write-Host "`n== $Name ==" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) { $Failed.Add($Name) }
}

Push-Location $RepoRoot
try {
    Invoke-Check "Backend compilation" { & $PythonPath -m compileall -q backend/app backend/scripts backend/tests }
    Invoke-Check "Backend tests" { Push-Location backend; try { & $PythonPath -m pytest -q } finally { Pop-Location } }
    Invoke-Check "Frontend lint" { Push-Location frontend; try { npm run lint } finally { Pop-Location } }
    Invoke-Check "Frontend type checking" { Push-Location frontend; try { npm run typecheck } finally { Pop-Location } }
    Invoke-Check "Frontend tests" { Push-Location frontend; try { npm test } finally { Pop-Location } }
    Invoke-Check "Frontend build" { Push-Location frontend; try { npm run build } finally { Pop-Location } }
    Invoke-Check "Extension lint" { Push-Location extension; try { npm run lint } finally { Pop-Location } }
    Invoke-Check "Extension type checking" { Push-Location extension; try { npm run typecheck } finally { Pop-Location } }
    Invoke-Check "Extension tests" { Push-Location extension; try { npm test } finally { Pop-Location } }
    Invoke-Check "Extension build" { Push-Location extension; try { npm run build } finally { Pop-Location } }
}
finally { Pop-Location }

if ($Failed.Count -gt 0) {
    Write-Error ("Required checks failed: " + ($Failed -join ", "))
    exit 1
}
Write-Host "All required checks passed." -ForegroundColor Green
