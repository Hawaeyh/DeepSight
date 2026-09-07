from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.database import create_database_engine, get_db
from app.core.security import create_access_token
from app.database.migrations import upgrade_database
from app.main import app
from app.models.analysis import Analysis
from app.models.user import User


@pytest.fixture
def security_context(tmp_path: Path) -> Iterator[SimpleNamespace]:
    database_url = f"sqlite:///{(tmp_path / 'security.db').as_posix()}"
    upgrade_database("head", database_url)
    engine = create_database_engine(database_url)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_database():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_database
    database = session_factory()
    user_a = User(full_name="User A", email="a@example.com", password="hash")
    user_b = User(full_name="User B", email="b@example.com", password="hash")
    database.add_all([user_a, user_b])
    database.commit()
    database.refresh(user_a)
    database.refresh(user_b)

    def headers(user: User) -> dict[str, str]:
        token = create_access_token({"sub": user.email, "uid": user.id})
        return {"Authorization": f"Bearer {token}"}

    def create_analysis(owner: User | None, file_path: Path, **overrides) -> Analysis:
        values = {
            "owner_user_id": owner.id if owner else None,
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_type": "Image",
            "source": "web",
            "prediction": "Real",
            "confidence": 90.0,
            "risk_level": "Low",
            "model_name": "test-model",
            "model_version": "1",
            "device": "cpu",
            "processing_time": 0.1,
            "status": "Completed",
        }
        values.update(overrides)
        analysis = Analysis(**values)
        database.add(analysis)
        database.commit()
        database.refresh(analysis)
        return analysis

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            database=database,
            headers=headers,
            user_a=user_a,
            user_b=user_b,
            create_analysis=create_analysis,
            tmp_path=tmp_path,
        )

    database.close()
    app.dependency_overrides.clear()
    engine.dispose()
