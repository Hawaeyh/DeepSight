[CmdletBinding()]
param([string]$OutputPath)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not $OutputPath) { $OutputPath = "$RepoRoot\backend\reports\database-integrity.json" }
& $PythonPath "$RepoRoot\backend\scripts\audit_database_integrity.py" --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "Database integrity problems were found. Review $OutputPath." }
