import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_ROOT = Path(tempfile.mkdtemp(prefix="deepsight-tests-"))
os.environ.update(
    {
        "APP_ENV": "testing",
        "DATABASE_URL": f"sqlite:///{(TEST_ROOT / 'test.db').as_posix()}",
        "SECRET_KEY": "testing-only-secret-key-at-least-32-characters",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "5",
        "FIREBASE_ENABLED": "false",
        "FIREBASE_CREDENTIALS_PATH": "",
        "FIREBASE_PROJECT_ID": "",
        "MODEL_LOADING": "disabled",
        "LOCAL_STORAGE_ROOT": str(TEST_ROOT / "storage"),
        "REPORT_ROOT": str(TEST_ROOT / "reports"),
        "LOG_LEVEL": "WARNING",
    }
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
