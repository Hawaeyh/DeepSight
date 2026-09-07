[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StateFile = Join-Path $RepoRoot ".run\processes.json"
if (-not (Test-Path $StateFile)) { Write-Host "No DeepSight process state file exists."; exit 0 }

$state = Get-Content -Raw $StateFile | ConvertFrom-Json
foreach ($entry in $state.processes) {
    $process = Get-Process -Id ([int]$entry.id) -ErrorAction SilentlyContinue
    if (-not $process) { Write-Host "$($entry.kind) process is already stopped."; continue }
    $expectedStart = [DateTime]::Parse($entry.startedAt)
    if ($process.ProcessName -notin @("pwsh", "powershell") -or [Math]::Abs(($process.StartTime - $expectedStart).TotalSeconds) -gt 2) {
        Write-Warning "Refusing to stop PID $($entry.id): process identity no longer matches recorded $($entry.kind) process."
        continue
    }
    Stop-Process -Id $process.Id -Force
    Write-Host "Stopped $($entry.kind) process $($process.Id)."
}
Remove-Item -LiteralPath $StateFile
