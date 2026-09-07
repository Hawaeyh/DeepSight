from sqlalchemy.orm import Session

from app.models.notification import AuditEvent, Notification


class NotificationService:
    @staticmethod
    def create(db: Session, user_id: int | None, category: str, title: str, message: str, data: dict | None = None) -> Notification | None:
        if user_id is None:
            return None
        item = Notification(user_id=user_id, category=category, title=title, message=message, data=data)
        db.add(item)
        return item


class AuditService:
    @staticmethod
    def record(db: Session, actor_user_id: int | None, action: str, target_type: str | None = None, target_id: str | None = None, outcome: str = "success", details: dict | None = None) -> AuditEvent:
        event = AuditEvent(actor_user_id=actor_user_id, action=action, target_type=target_type, target_id=target_id, outcome=outcome, details=details)
        db.add(event)
        return event
