from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.guest_session_service import GuestSessionService
from app.api.dependencies import get_current_user, get_optional_guest_session
from app.models.analysis import Analysis
from app.models.guest_session import GuestSession
from app.models.user import User


router = APIRouter(prefix="/guest", tags=["Guest Sessions"])


@router.post("/session", status_code=201)
def create_guest_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    raw_token = request.cookies.get(GuestSessionService.cookie_name())
    if raw_token:
        try:
            session = GuestSessionService.verify(db, raw_token)
            return {"expires_at": session.expires_at, "analysis_limit": 2}
        except HTTPException:
            response.delete_cookie(GuestSessionService.cookie_name(), path="/")
    session = GuestSessionService.create(db, request, response)
    return {"expires_at": session.expires_at, "analysis_limit": 2}


@router.post("/transfer")
def transfer_guest_analyses(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    guest_session: GuestSession | None = Depends(get_optional_guest_session),
):
    if guest_session is None:
        raise HTTPException(status_code=401, detail="A valid guest session is required.")
    if guest_session.transferred_at is not None:
        raise HTTPException(status_code=409, detail="Guest analyses were already transferred.")
    transferred = (
        db.query(Analysis)
        .filter(
            Analysis.guest_session_id == guest_session.id,
            Analysis.owner_user_id.is_(None),
        )
        .update(
            {Analysis.owner_user_id: user.id, Analysis.guest_session_id: None},
            synchronize_session=False,
        )
    )
    guest_session.transferred_at = datetime.utcnow()
    guest_session.transferred_user_id = user.id
    db.commit()
    response.delete_cookie(GuestSessionService.cookie_name(), path="/")
    return {"transferred": transferred}
