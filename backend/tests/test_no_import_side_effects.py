import os
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


def isolated_environment(tmp_path: Path, database_name: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "APP_ENV": "testing",
            "DATABASE_URL": f"sqlite:///{(tmp_path / database_name).as_posix()}",
            "SECRET_KEY": "subprocess-test-secret-key-at-least-32-characters",
            "FIREBASE_ENABLED": "false",
            "MODEL_LOADING": "disabled",
            "LOCAL_STORAGE_ROOT": str(tmp_path / "storage"),
            "REPORT_ROOT": str(tmp_path / "reports"),
        }
    )
    return environment


def run_python(code: str, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_import_does_not_create_database_or_storage(tmp_path: Path) -> None:
    database_path = tmp_path / "import-only.db"
    storage_path = tmp_path / "storage"
    result = run_python("import app.main", isolated_environment(tmp_path, database_path.name))

    assert result.returncode == 0, result.stderr
    assert not database_path.exists()
    assert not storage_path.exists()


def test_import_does_not_create_admin_or_reset_existing_password(tmp_path: Path) -> None:
    code = """
from app.core.database import SessionLocal
from app.database.initialization import initialize_test_database
from app.models.user import User

initialize_test_database()
db = SessionLocal()
db.add(User(email='existing@example.com', full_name='Existing', password='unchanged-hash', role='user', is_active=True))
db.commit()
before_count = db.query(User).count()
db.close()

import app.main

db = SessionLocal()
user = db.query(User).filter(User.email == 'existing@example.com').one()
assert db.query(User).count() == before_count
assert user.password == 'unchanged-hash'
assert user.role == 'user'
db.close()
"""
    result = run_python(code, isolated_environment(tmp_path, "existing.db"))

    assert result.returncode == 0, result.stderr
