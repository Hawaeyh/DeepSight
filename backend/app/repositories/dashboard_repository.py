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

    @staticmethod
    def model_metrics(db: Session):
        rows = (
            db.query(
                Analysis.model_name,
                func.count(Analysis.id),
                func.avg(Analysis.confidence),
            )
            .group_by(Analysis.model_name)
            .all()
        )
        total = sum(row[1] for row in rows)
        metrics = []

        for model_name, usage_count, average_confidence in rows:
            verified = (
                db.query(Analysis)
                .filter(
                    Analysis.model_name == model_name,
                    Analysis.verified_result.isnot(None),
                )
                .all()
            )
            correct = sum(item.prediction == item.verified_result for item in verified)
            true_positive = sum(
                item.prediction == "Fake" and item.verified_result == "Fake"
                for item in verified
            )
            false_positive = sum(
                item.prediction == "Fake" and item.verified_result != "Fake"
                for item in verified
            )
            false_negative = sum(
                item.prediction != "Fake" and item.verified_result == "Fake"
                for item in verified
            )
            precision_denominator = true_positive + false_positive
            recall_denominator = true_positive + false_negative
            precision = true_positive / precision_denominator if precision_denominator else None
            recall = true_positive / recall_denominator if recall_denominator else None
            f1_score = (
                2 * precision * recall / (precision + recall)
                if precision is not None and recall is not None and precision + recall
                else None
            )
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
