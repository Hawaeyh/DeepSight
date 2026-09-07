from datetime import datetime

from sqlalchemy.orm import Query, Session

from app.api.dependencies import AnalysisPrincipal
from app.models.analysis import Analysis


class AnalysisRepository:
    @staticmethod
    def create(db: Session, analysis: Analysis) -> Analysis:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def _accessible_query(
        db: Session, principal: AnalysisPrincipal
    ) -> Query[Analysis]:
        query = db.query(Analysis)
        if principal.owner_user_id is not None:
            return query.filter(Analysis.owner_user_id == principal.owner_user_id)
        return query.filter(Analysis.guest_session_id == principal.guest_session_id)

    @classmethod
    def get_accessible(
        cls, db: Session, analysis_id: int, principal: AnalysisPrincipal
    ) -> Analysis | None:
        return cls._accessible_query(db, principal).filter(Analysis.id == analysis_id).first()

    @staticmethod
    def get_owned(
        db: Session, analysis_id: int, owner_user_id: int
    ) -> Analysis | None:
        return (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id, Analysis.owner_user_id == owner_user_id)
            .first()
        )

    @staticmethod
    def list_owned(
        db: Session,
        owner_user_id: int,
        *,
        offset: int = 0,
        limit: int = 100,
        media_type: str | None = None,
        prediction: str | None = None,
        filename: str | None = None,
        source: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        newest_first: bool = True,
    ) -> list[Analysis]:
        query = db.query(Analysis).filter(Analysis.owner_user_id == owner_user_id)
        if media_type:
            query = query.filter(Analysis.file_type == media_type)
        if prediction:
            query = query.filter(Analysis.prediction == prediction)
        if filename:
            query = query.filter(Analysis.filename.ilike(f"%{filename}%"))
        if source:
            query = query.filter(Analysis.source == source)
        if created_from:
            query = query.filter(Analysis.created_at >= created_from)
        if created_to:
            query = query.filter(Analysis.created_at <= created_to)
        ordering = Analysis.created_at.desc() if newest_first else Analysis.created_at.asc()
        return query.order_by(ordering).offset(offset).limit(limit).all()

    @staticmethod
    def count_owned(
        db: Session,
        owner_user_id: int,
        *,
        media_type: str | None = None,
        prediction: str | None = None,
        filename: str | None = None,
        source: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        query = db.query(Analysis).filter(Analysis.owner_user_id == owner_user_id)
        if media_type:
            query = query.filter(Analysis.file_type == media_type)
        if prediction:
            query = query.filter(Analysis.prediction == prediction)
        if filename:
            query = query.filter(Analysis.filename.ilike(f"%{filename}%"))
        if source:
            query = query.filter(Analysis.source == source)
        if created_from:
            query = query.filter(Analysis.created_at >= created_from)
        if created_to:
            query = query.filter(Analysis.created_at <= created_to)
        return query.count()

    @classmethod
    def delete_accessible(
        cls, db: Session, analysis_id: int, principal: AnalysisPrincipal
    ) -> Analysis | None:
        analysis = cls.get_accessible(db, analysis_id, principal)
        if analysis is not None:
            db.delete(analysis)
            db.commit()
        return analysis

    @staticmethod
    def total_count(db: Session) -> int:
        return db.query(Analysis).count()
