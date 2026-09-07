[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location "$RepoRoot\extension"
try {
    if (-not (Test-Path package-lock.json)) { npm install }
    npm run build
}
finally { Pop-Location }
Write-Host "Open chrome://extensions, enable Developer mode, and load unpacked: $RepoRoot\extension\dist"
Write-Host "Edit extension/config.js before building when the API is not http://127.0.0.1:8000/api/v1."
