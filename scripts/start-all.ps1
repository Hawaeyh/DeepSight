[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDirectory = Join-Path $RepoRoot ".run"
New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null

& "$PSScriptRoot\verify-environment.ps1" -RequireAvailablePorts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& "$PSScriptRoot\start-redis.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$backend = Start-Process pwsh -ArgumentList @("-NoProfile", "-File", "$PSScriptRoot\start-backend.ps1") -WindowStyle Hidden -PassThru
$frontend = Start-Process pwsh -ArgumentList @("-NoProfile", "-File", "$PSScriptRoot\start-frontend.ps1") -WindowStyle Hidden -PassThru
$worker = Start-Process pwsh -ArgumentList @("-NoProfile", "-File", "$PSScriptRoot\start-worker.ps1") -WindowStyle Hidden -PassThru

@{
    createdAt = (Get-Date).ToString("o")
    processes = @(
        @{ kind = "backend"; id = $backend.Id; startedAt = $backend.StartTime.ToString("o") },
        @{ kind = "frontend"; id = $frontend.Id; startedAt = $frontend.StartTime.ToString("o") },
        @{ kind = "worker"; id = $worker.Id; startedAt = $worker.StartTime.ToString("o") }
    )
} | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 "$RunDirectory\processes.json"

Write-Host "Backend process opened: http://127.0.0.1:8000"
Write-Host "Frontend process opened: http://127.0.0.1:5173"
Write-Host "Celery video worker process opened."
Write-Host "Processes opening does not prove health. Check with:"
Write-Host "Invoke-RestMethod http://127.0.0.1:8000/api/v1/health"
