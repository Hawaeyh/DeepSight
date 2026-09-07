[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not (Test-Path "$RepoRoot\frontend\.env")) { throw "frontend/.env is missing." }

Push-Location "$RepoRoot\frontend"
try {
    if (-not (Test-Path node_modules)) { npm install }
    npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
}
finally { Pop-Location }
