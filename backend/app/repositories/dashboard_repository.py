from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis import Analysis


class DashboardRepository:

    # ==========================================
    # OVERVIEW
    # ==========================================

    @staticmethod
    def total_detection(db: Session):
        return db.query(Analysis).count()

    @staticmethod
    def total_image(db: Session):
        return (
            db.query(Analysis)
            .filter(Analysis.file_type == "Image")
            .count()
        )

    @staticmethod
    def total_video(db: Session):
        return (
            db.query(Analysis)
            .filter(Analysis.file_type == "Video")
            .count()
        )

    @staticmethod
    def total_fake(db: Session):
        return (
            db.query(Analysis)
            .filter(Analysis.prediction == "Fake")
            .count()
        )

    @staticmethod
    def total_real(db: Session):
        return (
            db.query(Analysis)
            .filter(Analysis.prediction == "Real")
            .count()
        )

    @staticmethod
    def average_confidence(db: Session):
        value = (
            db.query(
                func.avg(
                    Analysis.confidence
                )
            )
            .scalar()
        )

        return round(value or 0, 2)

    @staticmethod
    def average_processing_time(db: Session):
        value = (
            db.query(
                func.avg(
                    Analysis.processing_time
                )
            )
            .scalar()
        )

        return round(value or 0, 4)

    @staticmethod
    def latest_detection(db: Session):
        return (
            db.query(Analysis)
            .order_by(
                Analysis.created_at.desc()
            )
            .first()
        )

    # ==========================================
    # TODAY
    # ==========================================

    @staticmethod
    def today_detection(db: Session):

        today = datetime.utcnow().date()

        return (
            db.query(Analysis)
            .filter(
                func.date(
                    Analysis.created_at
                ) == today
            )
            .count()
        )

    # ==========================================
    # THIS WEEK
    # ==========================================

    @staticmethod
    def week_detection(db: Session):

        week = datetime.utcnow() - timedelta(days=7)

        return (
            db.query(Analysis)
            .filter(
                Analysis.created_at >= week
            )
            .count()
        )

    # ==========================================
    # TREND
    # ==========================================

    @staticmethod
    def trend(db: Session):

        rows = (
            db.query(
                func.date(
                    Analysis.created_at
                ),
                func.count(
                    Analysis.id
                ),
            )
            .group_by(
                func.date(
                    Analysis.created_at
                )
            )
            .order_by(
                func.date(
                    Analysis.created_at
                )
            )
            .all()
        )

        return [
            {
                "date": str(row[0]),
                "count": row[1],
            }
            for row in rows
        ]

    # ==========================================
    # DISTRIBUTION
    # ==========================================

    @staticmethod
    def distribution(db: Session):

        total = DashboardRepository.total_detection(db)

        fake = DashboardRepository.total_fake(db)
        real = DashboardRepository.total_real(db)
        image = DashboardRepository.total_image(db)
        video = DashboardRepository.total_video(db)

        return {

            "fake": fake,

            "real": real,

            "image": image,

            "video": video,

            "fakePercentage":
                round(fake / total * 100, 2)
                if total else 0,

            "realPercentage":
                round(real / total * 100, 2)
                if total else 0,

            "imagePercentage":
                round(image / total * 100, 2)
                if total else 0,

            "videoPercentage":
                round(video / total * 100, 2)
                if total else 0,
        }

    # ==========================================
    # RECENT
    # ==========================================

    @staticmethod
    def recent_detection(
        db: Session,
        limit: int = 10,
    ):

        return (
            db.query(Analysis)
            .order_by(
                Analysis.created_at.desc()
            )
            .limit(limit)
            .all()
        )