from sqlalchemy.orm import Session
from app.models.analysis import Analysis


class HistoryRepository:

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(Analysis)
            .order_by(Analysis.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, analysis_id: int):

        return (
            db.query(Analysis)
            .filter(
                Analysis.id == analysis_id
            )
            .first()
        )

    @staticmethod
    def delete(db: Session, analysis_id: int):

        analysis = (
            db.query(Analysis)
            .filter(
                Analysis.id == analysis_id
            )
            .first()
        )

        if analysis:

            db.delete(analysis)

            db.commit()

        return analysis