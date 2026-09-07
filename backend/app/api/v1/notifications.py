from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User


router = APIRouter(prefix="/notifications", tags=["Notifications"])


def serialize(item: Notification) -> dict:
    return {"id": item.id, "category": item.category, "title": item.title, "message": item.message, "data": item.data, "isRead": item.is_read, "createdAt": item.created_at}


@router.get("")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return [serialize(item) for item in items]


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if item is None: raise HTTPException(status_code=404, detail="Notification not found.")
    item.is_read = True; db.commit(); db.refresh(item)
    return serialize(item)


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    updated = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).update({"is_read": True})
    db.commit(); return {"updated": updated}


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if item is None: raise HTTPException(status_code=404, detail="Notification not found.")
    db.delete(item); db.commit(); return {"message": "Notification deleted."}
