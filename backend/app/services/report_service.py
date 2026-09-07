class ReportService:
    @staticmethod
    def create(analysis, db=None):
        from app.utils.pdf_generator import generate_report
        from app.core.paths import REPORT_DIR
        destination = REPORT_DIR / f"analysis_{analysis.id}.pdf"
        if destination.is_file() and analysis.updated_at and destination.stat().st_mtime >= analysis.updated_at.timestamp():
            return destination
        details = {}
        if db is not None:
            from app.models.video_job import VideoFrame, VideoJob, VideoSegment
            job = db.query(VideoJob).filter(VideoJob.analysis_id == analysis.id).first()
            if job:
                details["frames"] = db.query(VideoFrame).filter(VideoFrame.video_job_id == job.id).order_by(VideoFrame.timestamp_ms).limit(120).all()
                details["segments"] = db.query(VideoSegment).filter(VideoSegment.video_job_id == job.id).order_by(VideoSegment.start_timestamp_ms).all()
                details["job"] = job
            from app.models.extension_session import ExtensionVideoSession
            extension = db.query(ExtensionVideoSession).filter(ExtensionVideoSession.analysis_id == analysis.id).first()
            if extension: details["extension"] = extension; details["extension_frames"] = extension.predictions or []
        return generate_report(analysis, details)
