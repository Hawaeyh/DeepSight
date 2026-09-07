export type VideoJobStatus = "pending" | "queued" | "processing" | "completed" | "failed" | "cancel_requested" | "cancelled";

export interface VideoJob {
    job_id: string;
    analysis_id: number;
    status: VideoJobStatus;
    progress: number;
    stage: string;
    processed_frames: number;
    selected_frames: number;
    detected_tracks: number;
    result: "likely_real" | "likely_manipulated" | "inconclusive" | null;
    overall_confidence: number | null;
    primary_track_id: number | null;
    error_code: string | null;
    error_message: string | null;
    metadata: { display_label?: string; suspicious_frames?: number; sampling_notice?: string } | null;
}

export interface VideoFrameResult {
    id: number;
    timestamp_ms: number;
    frame_number: number;
    track_id: number | null;
    quality_score: number;
    prediction: "Real" | "Fake";
    fake_probability: number;
    confidence: number;
    sampling_reason: string;
    thumbnail_url: string;
}

export interface VideoTrack { id:number; track_number:number; frame_count:number; overall_result:string; overall_confidence:number; median_fake_probability:number; maximum_fake_probability:number; suspicious_frame_count:number }
export interface VideoSegment { id:number; track_id:number|null; start_timestamp_ms:number; end_timestamp_ms:number; result:string; confidence:number; frame_count:number }
