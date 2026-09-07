[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Push-Location $RepoRoot
try {
    if (-not (Test-Path $PythonPath)) { py -3.11 -m venv .venv }
    & $PythonPath -m pip install --upgrade pip
    & $PythonPath -m pip install -r backend/requirements-dev.txt

    if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env; Write-Host "Created backend/.env from example." }
    else { Write-Host "Preserved existing backend/.env." }
    if (-not (Test-Path frontend/.env)) { Copy-Item frontend/.env.example frontend/.env; Write-Host "Created frontend/.env from example." }
    else { Write-Host "Preserved existing frontend/.env." }

    Push-Location frontend
    try { npm install }
    finally { Pop-Location }
    Push-Location extension
    try { npm install }
    finally { Pop-Location }

    @(
        "backend/uploads/images",
        "backend/uploads/videos",
        "backend/uploads/video_frames",
        "backend/reports",
        "datasets/hard_examples"
    ) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
}
finally { Pop-Location }

Write-Host "Setup complete. Review backend/.env and frontend/.env before starting services."
Write-Host "Create the schema explicitly with: python backend/scripts/init_database.py"
Write-Host "No administrator or user data was created."
