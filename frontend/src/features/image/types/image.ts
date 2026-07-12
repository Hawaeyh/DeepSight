export interface ImageDetectionResponse {

    id: number;

    filename: string;

    file_path: string;

    file_type: string;

    file_extension: string;

    file_size: number;

    prediction: string;

    confidence: number;

    real_probability: number;

    fake_probability: number;

    deepfake_type: string | null;

    type_confidence: number | null;

    risk_level: string;

    model_name: string;

    model_version: string;

    device: string;

    processing_time: number;

    status: string;

    face_detected: boolean;

    face_count: number;

    image_width: number;

    image_height: number;

    created_at: string;

    updated_at: string;

}