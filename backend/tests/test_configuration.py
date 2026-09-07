import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings


def test_testing_configuration_is_isolated() -> None:
    assert settings.APP_ENV == "testing"
    assert settings.DATABASE_URL.startswith("sqlite:///")
    assert "deepsight-tests-" in settings.DATABASE_URL
    assert settings.FIREBASE_ENABLED is False
    assert settings.MODEL_LOADING == "disabled"


@pytest.mark.parametrize(
    ("database_url", "secret_key"),
    [("", "x" * 32), ("sqlite:///test.db", "too-short")],
)
def test_invalid_critical_configuration_has_clear_errors(
    database_url: str,
    secret_key: str,
) -> None:
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL=database_url, SECRET_KEY=secret_key)
