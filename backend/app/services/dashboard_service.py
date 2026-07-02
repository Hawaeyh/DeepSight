from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    # ==========================================
    # OVERVIEW
    # ==========================================

    @staticmethod
    def overview(db: Session):

        latest = DashboardRepository.latest_detection(db)

        distribution = DashboardRepository.distribution(db)

        return {

            "totalDetection":
                DashboardRepository.total_detection(db),

            "totalImages":
                DashboardRepository.total_image(db),

            "totalVideos":
                DashboardRepository.total_video(db),

            "totalFake":
                DashboardRepository.total_fake(db),

            "totalReal":
                DashboardRepository.total_real(db),

            "averageConfidence":
                DashboardRepository.average_confidence(db),

            "averageProcessingTime":
                DashboardRepository.average_processing_time(db),

            "todayDetection":
                DashboardRepository.today_detection(db),

            "weekDetection":
                DashboardRepository.week_detection(db),

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
    def trend(db: Session):

        return DashboardRepository.trend(db)

    # ==========================================
    # DISTRIBUTION
    # ==========================================

    @staticmethod
    def distribution(db: Session):

        return DashboardRepository.distribution(db)

    # ==========================================
    # RECENT
    # ==========================================

    @staticmethod
    def recent(db: Session):

        analyses = DashboardRepository.recent_detection(db)

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