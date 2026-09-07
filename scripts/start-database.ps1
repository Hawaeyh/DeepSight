[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or is unavailable on PATH."
}

Push-Location $RepoRoot
try {
    $DatabaseUser = if ($env:DEEPSIGHT_POSTGRES_USER) { $env:DEEPSIGHT_POSTGRES_USER } else { "deepsight" }
    $DatabaseName = if ($env:DEEPSIGHT_POSTGRES_DB) { $env:DEEPSIGHT_POSTGRES_DB } else { "deepsight" }
    $running = docker compose ps --status running --services 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose is unavailable." }
    if ($running -notcontains "postgres") {
        $listener = Get-NetTCPConnection -State Listen -LocalPort 5432 -ErrorAction SilentlyContinue
        if ($listener) { throw "Port 5432 is already occupied by a process outside this Compose project." }
        docker compose up -d postgres
        if ($LASTEXITCODE -ne 0) { throw "PostgreSQL container failed to start." }
    }

    $ready = $false
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        docker compose exec -T postgres pg_isready -U $DatabaseUser -d $DatabaseName *> $null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) { throw "PostgreSQL did not become ready within 60 seconds." }
    Write-Host "PostgreSQL development service is ready on localhost:5432."
}
finally { Pop-Location }
