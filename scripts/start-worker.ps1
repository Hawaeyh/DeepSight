[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) { throw "Virtual environment missing." }
$connection = Test-NetConnection 127.0.0.1 -Port 6379 -WarningAction SilentlyContinue
if (-not $connection.TcpTestSucceeded) { throw "Redis is unavailable. Run scripts/start-redis.ps1." }
$env:REDIS_URL = if ($env:REDIS_URL) { $env:REDIS_URL } else { "redis://127.0.0.1:6379/0" }
$env:CELERY_BROKER_URL = if ($env:CELERY_BROKER_URL) { $env:CELERY_BROKER_URL } else { $env:REDIS_URL }
$env:CELERY_RESULT_BACKEND = if ($env:CELERY_RESULT_BACKEND) { $env:CELERY_RESULT_BACKEND } else { "redis://127.0.0.1:6379/1" }
Push-Location "$RepoRoot\backend"
try { & $PythonPath -m celery -A app.workers.celery_app worker --loglevel=info --pool=solo }
finally { Pop-Location }
