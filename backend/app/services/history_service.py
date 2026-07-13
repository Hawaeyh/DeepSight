from sqlalchemy.orm import Session

from app.repositories.history_repository import (
    HistoryRepository,
)
from app.services.firebase_service import FirebaseService


class HistoryService:

    @staticmethod
    def get_all(db: Session):

        return HistoryRepository.get_all(db)

    @staticmethod
    def get_by_id(
        db: Session,
        analysis_id: int,
    ):

        return HistoryRepository.get_by_id(
            db,
            analysis_id,
        )

    @staticmethod
    def delete(
        db: Session,
        analysis_id: int,
    ):

        deleted = HistoryRepository.delete(
            db,
            analysis_id,
        )

        if deleted:
            FirebaseService.delete_analysis(analysis_id)

        return deleted

    @staticmethod
    def verify(db: Session, analysis_id: int, verified_result: str, remarks: str | None = None):
        analysis = HistoryRepository.verify(db, analysis_id, verified_result, remarks)
        if analysis:
            FirebaseService.save_analysis(analysis)
        return analysis
