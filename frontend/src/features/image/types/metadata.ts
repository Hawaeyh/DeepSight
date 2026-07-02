export type PredictionType = "Real" | "Fake";

export type RiskLevel = "Low" | "Medium" | "High";

export interface ImageInformation {
    filename: string;
    width: number;
    height: number;
    faceDetected: boolean;
    faceCount: number;
}

export interface PredictionInformation {
    prediction: PredictionType;
    confidence: number;
    probabilityReal: number;
    probabilityFake: number;
    riskLevel: RiskLevel;
    recommendation: string;
}

export interface ModelInformation {
    name: string;
    version: string;
    device: string;
    processingTime: number;
}

export interface ImageDetectionResponse {
    analysisId: number;

    image: ImageInformation;

    prediction: PredictionInformation;

    model: ModelInformation;

    createdAt: string;
}