from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {
        "status": "online",
        "system": "ML7-VIDS DeepSight API",
        "version": "1.0.0"
    }