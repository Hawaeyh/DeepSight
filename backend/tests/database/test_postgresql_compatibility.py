import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateTable

from app.core.database import Base, create_database_engine
from app.database.initialization import register_models
from app.database.migrations import current_revision, upgrade_database


def test_all_model_tables_compile_for_postgresql():
    register_models()
    for table in Base.metadata.sorted_tables:
        assert "CREATE TABLE" in str(CreateTable(table).compile(dialect=postgresql.dialect()))


@pytest.mark.postgresql
def test_isolated_postgresql_upgrade_and_schema():
    url = os.getenv("POSTGRES_TEST_DATABASE_URL")
    if not url:
        pytest.skip("POSTGRES_TEST_DATABASE_URL is not configured")
    upgrade_database("head", url)
    engine = create_database_engine(url)
    try:
        assert current_revision(engine) == "0003_security_ownership"
        assert "analysis_feedback" in inspect(engine).get_table_names()
        foreign_keys = inspect(engine).get_foreign_keys("analysis_feedback")
        assert foreign_keys[0]["referred_table"] == "analysis"
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM users WHERE email IN ('pg-test@example.com','pg-admin@example.com')"))
            connection.execute(text("INSERT INTO users (email,full_name,password) VALUES ('pg-test@example.com','PG Test','hash')"))
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text("INSERT INTO users (email,full_name,password) VALUES ('pg-test@example.com','Duplicate','hash')"))
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text("INSERT INTO analysis_feedback (analysis_id,is_correct,status,created_at) VALUES (2147483647,true,'reviewed',CURRENT_TIMESTAMP)"))

        environment = os.environ.copy()
        environment.update({"DATABASE_URL": url, "APP_ENV": "development"})
        backend = Path(__file__).resolve().parents[2]
        seed = subprocess.run([sys.executable, "scripts/seed_development.py"], cwd=backend, env=environment, capture_output=True, text=True, check=False)
        assert seed.returncode == 0, seed.stdout + seed.stderr
        admin = subprocess.run(
            [sys.executable, "scripts/create_admin.py", "--email", "pg-admin@example.com"],
            input="StrongPassword!123\nStrongPassword!123\n", cwd=backend, env=environment,
            capture_output=True, text=True, check=False,
        )
        assert admin.returncode == 0, admin.stdout + admin.stderr
        with engine.begin() as connection:
            created = connection.execute(text("SELECT role FROM users WHERE email='pg-admin@example.com'")).scalar_one()
            assert created == "admin"
            connection.execute(text("DELETE FROM users WHERE email IN ('pg-test@example.com','pg-admin@example.com')"))
    finally:
        engine.dispose()
