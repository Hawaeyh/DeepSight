from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import Analysis
from app.services.firebase_service import FirebaseService

router = APIRouter(prefix="/firebase", tags=["Firebase"])


@router.get("/status")
def firebase_status():
    return FirebaseService.status()


@router.post("/sync")
def sync_existing_analyses(db: Session = Depends(get_db)):
    status = FirebaseService.status()
    if not status["connected"]:
        raise HTTPException(status_code=503, detail=status["error"])

    analyses = db.query(Analysis).all()
    synced = sum(FirebaseService.save_analysis(item) for item in analyses)
    return {"total": len(analyses), "synced": synced}
