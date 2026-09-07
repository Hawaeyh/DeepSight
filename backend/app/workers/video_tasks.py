from datetime import datetime
from pathlib import Path
import shutil

import cv2
from celery.exceptions import SoftTimeLimitExceeded

from app.ai.model_status import ModelUnavailableError
from app.core.database import SessionLocal
from app.core.paths import VIDEO_FRAME_DIR, VIDEO_UPLOAD_DIR
from app.inference.face_tracker import IoUFaceTracker
from app.inference.frame_sampler import sample_video
from app.inference.video_aggregator import aggregate_frames
from app.models.analysis import Analysis
from app.models.video_job import VideoFaceTrack, VideoFrame, VideoJob, VideoSegment
from app.services.ai_service import AIService
from app.services.protected_file_service import contained_file
from app.services.subscription_service import SubscriptionService
from app.services.notification_service import NotificationService
from app.workers.celery_app import celery_app


def update(db, job, progress: int, stage: str) -> None:
    db.refresh(job)
    if job.status == "cancel_requested":
        raise InterruptedError
    job.status = "processing"
    job.progress = min(max(progress, 0), 99)
    job.current_stage = stage
    db.commit()


@celery_app.task(bind=True, name="deepsight.process_video")
def process_video_task(self, job_id: str) -> None:
    db = SessionLocal()
    frame_dir = VIDEO_FRAME_DIR / job_id
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if job is None:
        db.close()
        return
    try:
        source = contained_file(job.stored_file_key, VIDEO_UPLOAD_DIR)
        job.started_at = datetime.utcnow()
        update(db, job, 5, "Selecting representative frames")
        sampled = sample_video(str(source))
        if not sampled:
            raise ValueError("NO_FACE_DETECTED")
        job.selected_frame_count = len(sampled)
        db.commit()
        frame_dir.mkdir(parents=True, exist_ok=True)
        tracker = IoUFaceTracker()
        predictions = []
        for index, sampled_frame in enumerate(sampled):
            update(db, job, 15 + int(index / len(sampled) * 65), "Detecting faces and running inference")
            thumbnail = frame_dir / f"frame_{index:04d}.jpg"
            cv2.imwrite(str(thumbnail), sampled_frame.image)
            face_results = AIService.analyze_video_frame(str(thumbnail), "efficientnet")
            if not face_results:
                thumbnail.unlink(missing_ok=True)
                continue
            track_numbers = tracker.assign([result["selected_face_box"] for result in face_results], index)
            for result, track_number in zip(face_results, track_numbers):
                predictions.append({
                "frame_number": sampled_frame.frame_number, "timestamp_ms": sampled_frame.timestamp_ms,
                "track_id": track_number, "face_index": result.get("selected_face_index", 0),
                "sampling_reason": sampled_frame.reason, "quality_score": sampled_frame.quality_score,
                "prediction": result["prediction"], "fake_probability": result["fake_probability"],
                "confidence": result["confidence"], "thumbnail_key": str(thumbnail),
                "model_id": f"{result['model_name']}:{result['model_version']}",
                })
            job.processed_frame_count = len(predictions)
            db.commit()
        update(db, job, 85, "Aggregating predictions")
        aggregate = aggregate_frames(predictions)
        track_rows = {}
        for track in aggregate["tracks"]:
            items = [item for item in predictions if item["track_id"] == track["track_id"]]
            row = VideoFaceTrack(
                video_job_id=job.id, track_number=track["track_id"], first_timestamp_ms=min(i["timestamp_ms"] for i in items),
                last_timestamp_ms=max(i["timestamp_ms"] for i in items), frame_count=track["frames"],
                median_fake_probability=track["median_fake_probability"], maximum_fake_probability=track["maximum_fake_probability"],
                suspicious_frame_count=track["suspicious_frames"], overall_result=track["result"], overall_confidence=track["confidence"],
            )
            db.add(row); db.flush(); track_rows[track["track_id"]] = row.id
        for item in predictions:
            db.add(VideoFrame(video_job_id=job.id, track_id=track_rows[item.pop("track_id")], **item))
        for segment in aggregate["segments"]:
            db.add(VideoSegment(video_job_id=job.id, track_id=track_rows[segment["track_id"]], start_timestamp_ms=segment["start_timestamp_ms"], end_timestamp_ms=segment["end_timestamp_ms"], result=segment["result"], confidence=segment["confidence"], frame_count=segment["frame_count"]))
        job.detected_track_count = len(track_rows)
        job.overall_result = aggregate["result"]
        job.overall_confidence = aggregate["overall_confidence"]
        job.primary_track_id = track_rows[aggregate["primary_track_id"]]
        job.metadata_json = {"display_label": aggregate["display_label"], "suspicious_frames": aggregate["suspicious_frames"], "analysed_frames": aggregate["analysed_frames"], "sampling_notice": "Result is based on representative sampled frames, not every frame."}
        job.status = "completed"; job.progress = 100; job.current_stage = "Completed"; job.completed_at = datetime.utcnow()
        analysis = db.query(Analysis).filter(Analysis.id == job.analysis_id).one()
        analysis.prediction = {"likely_manipulated": "Fake", "likely_real": "Real", "inconclusive": "Inconclusive"}[aggregate["result"]]
        analysis.confidence = aggregate["overall_confidence"]
        analysis.status = "Completed"; analysis.frames_analyzed = len(predictions)
        analysis.fake_frames = aggregate["suspicious_frames"]; analysis.real_frames = len(predictions) - aggregate["suspicious_frames"]
        NotificationService.create(db, job.owner_user_id, "video_completed", "Video analysis completed", f"{job.original_filename} is ready.", {"jobId": job.id, "analysisId": job.analysis_id})
        SubscriptionService.complete_key(db, (job.metadata_json or {}).get("usage_reservation_key"))
        db.commit()
    except InterruptedError:
        SubscriptionService.release_key(db, (job.metadata_json or {}).get("usage_reservation_key"))
        job.status = "cancelled"; job.current_stage = "Cancelled"; job.cancelled_at = datetime.utcnow(); db.commit()
        shutil.rmtree(frame_dir, ignore_errors=True)
    except (SoftTimeLimitExceeded, ModelUnavailableError, ValueError) as error:
        SubscriptionService.release_key(db, (job.metadata_json or {}).get("usage_reservation_key"))
        job.status = "failed"; job.error_code = "TASK_TIMEOUT" if isinstance(error, SoftTimeLimitExceeded) else "MODEL_UNAVAILABLE" if isinstance(error, ModelUnavailableError) else str(error) if str(error) in {"NO_FACE_DETECTED"} else "INFERENCE_FAILED"
        job.error_message_safe = "Video processing could not be completed."; job.current_stage = "Failed"; NotificationService.create(db, job.owner_user_id, "video_failed", "Video analysis failed", f"{job.original_filename} could not be completed.", {"jobId": job.id}); db.commit()
        shutil.rmtree(frame_dir, ignore_errors=True)
    except Exception:
        SubscriptionService.release_key(db, (job.metadata_json or {}).get("usage_reservation_key"))
        job.status = "failed"; job.error_code = "INFERENCE_FAILED"; job.error_message_safe = "Video processing failed safely."; job.current_stage = "Failed"; NotificationService.create(db, job.owner_user_id, "video_failed", "Video analysis failed", f"{job.original_filename} could not be completed.", {"jobId": job.id}); db.commit()
        shutil.rmtree(frame_dir, ignore_errors=True)
    finally:
        db.close()
