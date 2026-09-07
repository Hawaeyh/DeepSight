[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker is required to start Redis." }
Push-Location $RepoRoot
try {
    docker compose up -d redis
    if ($LASTEXITCODE -ne 0) { throw "Redis container failed to start." }
    for ($attempt=1; $attempt -le 30; $attempt++) {
        docker compose exec -T redis redis-cli ping 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Host "Redis is ready on 127.0.0.1:6379."; exit 0 }
        Start-Sleep -Seconds 1
    }
    throw "Redis did not become ready."
} finally { Pop-Location }
