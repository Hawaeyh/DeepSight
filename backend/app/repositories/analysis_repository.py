from sqlalchemy.orm import Session

from app.models.analysis import Analysis


class AnalysisRepository:

    @staticmethod
    def create(
        db: Session,
        analysis: Analysis,
    ):

        db.add(analysis)

        db.commit()

        db.refresh(analysis)

        return analysis

    @staticmethod
    def get_all(
        db: Session,
    ):

        return (
            db.query(Analysis)
            .order_by(
                Analysis.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        analysis_id: int,
    ):

        return (
            db.query(Analysis)
            .filter(
                Analysis.id == analysis_id
            )
            .first()
        )

    @staticmethod
    def delete(
        db: Session,
        analysis_id: int,
    ):

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

    @staticmethod
    def total_count(
        db: Session,
    ):

        return (
            db.query(Analysis)
            .count()
        )