export interface Prediction {

    label: string;

    confidence: number;

    riskLevel: string;

}

export interface Probability {

    real: number;

    fake: number;

}

export interface Deepfake {

    type: string;

    confidence: number;

}

export interface AIModel {

    name: string;

    version: string;

    device: string;

}

export interface Processing {

    time: number;

}

export interface ImageInformation {

    filename: string;

    width: number;

    height: number;

    faceDetected: boolean;

    faceCount: number;

}

export interface ImageDetectionResponse {
    
    analysisId:number;

    prediction:string;

    confidence:number;

    riskLevel:string;

    recommendation:string;

    model:string;

    version:string;

    processingTime:number;

}