# Cleanup jobs

Preview with `.\.venv\Scripts\python.exe backend\scripts\run_cleanup.py --dry-run`. Apply only after reviewing storage with `--confirm`. Cleanup removes expired untransferred guest data, orphan reports, and derived frame directories for old failed/cancelled jobs. It preserves signed-in user source media and history.
