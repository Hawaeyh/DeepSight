import type { Analysis } from "./analysis";

export interface VideoFrameResult {
    index: number;
    timestamp: number;
    prediction: "Real" | "Fake";
    confidence: number;
    real_probability: number;
    fake_probability: number;
    thumbnail_url: string;
}

export interface VideoDetectionResponse extends Analysis {
    frames_analyzed: number;
    fake_frames: number;
    real_frames: number;
    video_duration: number;
    frame_results: VideoFrameResult[];
    summary: string;
}
