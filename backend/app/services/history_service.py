from sqlalchemy.orm import Session

from app.repositories.history_repository import (
    HistoryRepository,
)


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

        return HistoryRepository.delete(
            db,
            analysis_id,
        )