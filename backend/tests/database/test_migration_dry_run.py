import json
import os
import subprocess
import sys
from pathlib import Path


def test_sqlite_migration_dry_run_is_non_mutating(migrated_database, tmp_path: Path):
    url, _ = migrated_database
    source = Path(url.removeprefix("sqlite:///"))
    report = tmp_path / "report.json"
    environment = os.environ.copy()
    environment.pop("DATABASE_URL", None)
    result = subprocess.run(
        [sys.executable, "scripts/migrate_sqlite_to_postgresql.py", "--source", str(source), "--dry-run", "--report", str(report)],
        cwd=Path(__file__).resolve().parents[2], env=environment, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    contents = json.loads(report.read_text(encoding="utf-8"))
    assert contents["success"] is True
    assert all(value == 0 for value in contents["source"]["row_counts"].values())
