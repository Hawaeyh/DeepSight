from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis import Analysis


class DashboardRepository:
    @staticmethod
    def _owned(db: Session, owner_user_id: int):
        return db.query(Analysis).filter(Analysis.owner_user_id == owner_user_id)

    @classmethod
    def total_detection(cls, db: Session, owner_user_id: int) -> int:
        return cls._owned(db, owner_user_id).count()

    @classmethod
    def total_image(cls, db: Session, owner_user_id: int) -> int:
        return cls._owned(db, owner_user_id).filter(Analysis.file_type == "Image").count()

    @classmethod
    def total_video(cls, db: Session, owner_user_id: int) -> int:
        return cls._owned(db, owner_user_id).filter(Analysis.file_type == "Video").count()

    @classmethod
    def total_fake(cls, db: Session, owner_user_id: int) -> int:
        return cls._owned(db, owner_user_id).filter(Analysis.prediction == "Fake").count()

    @classmethod
    def total_real(cls, db: Session, owner_user_id: int) -> int:
        return cls._owned(db, owner_user_id).filter(Analysis.prediction == "Real").count()

    @classmethod
    def average_confidence(cls, db: Session, owner_user_id: int) -> float:
        value = cls._owned(db, owner_user_id).with_entities(func.avg(Analysis.confidence)).scalar()
        return round(value or 0, 2)

    @classmethod
    def average_processing_time(cls, db: Session, owner_user_id: int) -> float:
        value = cls._owned(db, owner_user_id).with_entities(func.avg(Analysis.processing_time)).scalar()
        return round(value or 0, 4)

    @classmethod
    def latest_detection(cls, db: Session, owner_user_id: int) -> Analysis | None:
        return cls._owned(db, owner_user_id).order_by(Analysis.created_at.desc()).first()

    @classmethod
    def today_detection(cls, db: Session, owner_user_id: int) -> int:
        today = datetime.utcnow().date()
        return cls._owned(db, owner_user_id).filter(func.date(Analysis.created_at) == today).count()

    @classmethod
    def week_detection(cls, db: Session, owner_user_id: int) -> int:
        week = datetime.utcnow() - timedelta(days=7)
        return cls._owned(db, owner_user_id).filter(Analysis.created_at >= week).count()

    @classmethod
    def trend(cls, db: Session, owner_user_id: int) -> list[dict]:
        rows = (
            cls._owned(db, owner_user_id)
            .with_entities(func.date(Analysis.created_at), func.count(Analysis.id))
            .group_by(func.date(Analysis.created_at))
            .order_by(func.date(Analysis.created_at))
            .all()
        )
        return [{"date": str(row[0]), "count": row[1]} for row in rows]

    @classmethod
    def distribution(cls, db: Session, owner_user_id: int) -> dict:
        total = cls.total_detection(db, owner_user_id)
        fake = cls.total_fake(db, owner_user_id)
        real = cls.total_real(db, owner_user_id)
        image = cls.total_image(db, owner_user_id)
        video = cls.total_video(db, owner_user_id)
        return {
            "fake": fake,
            "real": real,
            "image": image,
            "video": video,
            "fakePercentage": round(fake / total * 100, 2) if total else 0,
            "realPercentage": round(real / total * 100, 2) if total else 0,
            "imagePercentage": round(image / total * 100, 2) if total else 0,
            "videoPercentage": round(video / total * 100, 2) if total else 0,
        }

    @classmethod
    def recent_detection(
        cls, db: Session, owner_user_id: int, limit: int = 10
    ) -> list[Analysis]:
        return cls._owned(db, owner_user_id).order_by(Analysis.created_at.desc()).limit(limit).all()

    @classmethod
    def model_metrics(cls, db: Session, owner_user_id: int) -> list[dict]:
        rows = (
            cls._owned(db, owner_user_id)
            .with_entities(Analysis.model_name, func.count(Analysis.id), func.avg(Analysis.confidence))
            .group_by(Analysis.model_name)
            .all()
        )
        total = sum(row[1] for row in rows)
        metrics = []
        for model_name, usage_count, average_confidence in rows:
            verified = cls._owned(db, owner_user_id).filter(
                Analysis.model_name == model_name, Analysis.verified_result.isnot(None)
            ).all()
            correct = sum(item.prediction == item.verified_result for item in verified)
            true_positive = sum(item.prediction == "Fake" and item.verified_result == "Fake" for item in verified)
            false_positive = sum(item.prediction == "Fake" and item.verified_result != "Fake" for item in verified)
            false_negative = sum(item.prediction != "Fake" and item.verified_result == "Fake" for item in verified)
            precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else None
            recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else None
            f1_score = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else None
            metrics.append({
                "model": model_name,
                "usageCount": usage_count,
                "usagePercentage": round(usage_count / total * 100, 2) if total else 0,
                "averageConfidence": round(average_confidence or 0, 2),
                "verifiedSamples": len(verified),
                "accuracy": round(correct / len(verified) * 100, 2) if verified else None,
                "precision": round(precision * 100, 2) if precision is not None else None,
                "recall": round(recall * 100, 2) if recall is not None else None,
                "f1Score": round(f1_score * 100, 2) if f1_score is not None else None,
            })
        return metrics
