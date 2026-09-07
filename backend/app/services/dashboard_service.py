from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    # ==========================================
    # OVERVIEW
    # ==========================================

    @staticmethod
    def overview(db: Session, owner_user_id: int):

        latest = DashboardRepository.latest_detection(db, owner_user_id)

        distribution = DashboardRepository.distribution(db, owner_user_id)

        return {

            "totalDetection":
                DashboardRepository.total_detection(db, owner_user_id),

            "totalImages":
                DashboardRepository.total_image(db, owner_user_id),

            "totalVideos":
                DashboardRepository.total_video(db, owner_user_id),

            "totalFake":
                DashboardRepository.total_fake(db, owner_user_id),

            "totalReal":
                DashboardRepository.total_real(db, owner_user_id),

            "averageConfidence":
                DashboardRepository.average_confidence(db, owner_user_id),

            "averageProcessingTime":
                DashboardRepository.average_processing_time(db, owner_user_id),

            "todayDetection":
                DashboardRepository.today_detection(db, owner_user_id),

            "weekDetection":
                DashboardRepository.week_detection(db, owner_user_id),

            "latestPrediction":
                latest.prediction if latest else None,

            "latestConfidence":
                latest.confidence if latest else None,

            "latestModel":
                latest.model_name if latest else None,

            "latestVersion":
                latest.model_version if latest else None,

            "device":
                latest.device if latest else "CPU",

            "fakePercentage":
                distribution["fakePercentage"],

            "realPercentage":
                distribution["realPercentage"],

            "imagePercentage":
                distribution["imagePercentage"],

            "videoPercentage":
                distribution["videoPercentage"],
        }

    # ==========================================
    # TREND
    # ==========================================

    @staticmethod
    def trend(db: Session, owner_user_id: int):

        return DashboardRepository.trend(db, owner_user_id)

    # ==========================================
    # DISTRIBUTION
    # ==========================================

    @staticmethod
    def distribution(db: Session, owner_user_id: int):

        return DashboardRepository.distribution(db, owner_user_id)

    # ==========================================
    # RECENT
    # ==========================================

    @staticmethod
    def recent(db: Session, owner_user_id: int):

        analyses = DashboardRepository.recent_detection(db, owner_user_id)

        return [

            {

                "id": item.id,

                "filename": item.filename,

                "fileType": item.file_type,

                "prediction": item.prediction,

                "confidence": item.confidence,

                "riskLevel": item.risk_level,

                "model": item.model_name,

                "version": item.model_version,

                "createdAt": item.created_at,

            }

            for item in analyses

        ]

    @staticmethod
    def models(db: Session, owner_user_id: int):
        return DashboardRepository.model_metrics(db, owner_user_id)
