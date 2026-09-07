from fastapi import APIRouter, Depends

from app.ai.model_status import get_inference_device, get_model_catalog
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/models", tags=["Models"])


@router.get("")
def list_models():
    return {
        "device": get_inference_device(),
        "models": get_model_catalog(),
    }


@router.get("/available")
def available_models(_: User = Depends(get_current_user)):
    return [{"id": item["key"], "name": item["name"], "task": "binary", "version": item["version"], "status": "active" if item["available"] else "unavailable", "description": item["description"], "supported_media": ["image", "video", "webcam", "extension"], "minimum_plan": "starter", "is_default": item["key"] == "efficientnet"} for item in get_model_catalog() if item["available"]]
