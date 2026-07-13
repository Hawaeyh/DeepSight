from fastapi import APIRouter

from app.ai.models.model_loader import DEVICE, get_model_catalog

router = APIRouter(
    prefix="/models",
    tags=["Models"],
)


@router.get("")
def list_models():
    return {
        "device": str(DEVICE),
        "models": get_model_catalog(),
    }
