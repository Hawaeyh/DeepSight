import sys


def test_importing_application_succeeds_without_loading_models() -> None:
    from app.ai.model_status import get_model_load_status
    from app.main import app

    assert app.title == "DeepSight System API"
    assert get_model_load_status() == {
        "binary": "disabled",
        "multiclass": "disabled",
        "face_detector": "disabled",
    }
    assert "torch" not in sys.modules
    assert "timm" not in sys.modules
    assert "insightface" not in sys.modules
