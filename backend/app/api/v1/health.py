from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {
        "status": "online",
        "system": "DeepSight System API",
        "version": "1.0.0"
    }
