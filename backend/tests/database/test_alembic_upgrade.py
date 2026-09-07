import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect, text

from app.database.migrations import downgrade_database, upgrade_database


EXPECTED_TABLES = {
    "users", "analysis", "analysis_feedback", "account_entitlements", "detection_usage", "guest_sessions"
}


def test_empty_database_upgrades_to_head(migrated_database):
    _, engine = migrated_database
    assert EXPECTED_TABLES <= set(inspect(engine).get_table_names())


def test_downgrade_and_reupgrade_have_valid_logic(migrated_database):
    url, engine = migrated_database
    engine.dispose()
    downgrade_database("0001_initial_schema", url)
    upgrade_database("head", url)


def test_application_starts_after_migration(migrated_database):
    url, _ = migrated_database
    environment = os.environ.copy()
    environment["DATABASE_URL"] = url
    command = (
        "from fastapi.testclient import TestClient; from app.main import app; "
        "response=TestClient(app).get('/api/v1/health'); "
        "assert response.status_code == 200 and response.json()['database'] == 'ok'"
    )
    result = subprocess.run(
        [sys.executable, "-c", command], cwd=Path(__file__).resolve().parents[2],
        env=environment, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_security_migration_preserves_legacy_rows_as_unowned(tmp_path):
    url = f"sqlite:///{(tmp_path / 'legacy.db').as_posix()}"
    upgrade_database("0002_integrity_indexes", url)
    from app.core.database import create_database_engine

    engine = create_database_engine(url)
    with engine.begin() as connection:
        connection.execute(text(
            "INSERT INTO analysis (filename,file_path,file_type,prediction,confidence,risk_level,model_name,model_version,device,processing_time,status) "
            "VALUES ('legacy.jpg','legacy.jpg','Image','Real',90,'Low','m','1','cpu',.1,'Completed')"
        ))
    engine.dispose()
    upgrade_database("head", url)
    engine = create_database_engine(url)
    try:
        with engine.connect() as connection:
            row = connection.execute(text("SELECT owner_user_id, guest_session_id FROM analysis")).one()
            assert row == (None, None)
    finally:
        engine.dispose()
