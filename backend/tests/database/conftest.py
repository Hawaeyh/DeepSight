from pathlib import Path

import pytest

from app.core.database import create_database_engine
from app.database.migrations import upgrade_database


@pytest.fixture
def migrated_database(tmp_path: Path):
    url = f"sqlite:///{(tmp_path / 'migrated.db').as_posix()}"
    upgrade_database("head", url)
    target_engine = create_database_engine(url)
    try:
        yield url, target_engine
    finally:
        target_engine.dispose()
