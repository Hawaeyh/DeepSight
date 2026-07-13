export type PredictionType = "Real" | "Fake";

export type RiskLevel = "Low" | "Medium" | "High";

export interface Analysis {

    id: number;

    filename: string;

    file_path: string;

    file_type: string;

    file_extension: string;

    file_size: number;

    prediction: PredictionType;

    confidence: number;

    real_probability: number;

    fake_probability: number;

    deepfake_type: string | null;

    type_confidence: number | null;

    risk_level: RiskLevel;

    model_name: string;

    model_version: string;

    device: string;

    processing_time: number;

    status: string;

    face_detected: boolean;

    face_count: number;

    image_width: number;

    image_height: number;

    video_duration: number | null;

    frames_analyzed: number | null;

    fake_frames: number | null;

    real_frames: number | null;

    verified_result: string | null;

    remarks: string | null;

    created_at: string;

    updated_at: string;

}