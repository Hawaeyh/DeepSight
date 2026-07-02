export interface DashboardOverview {

    totalDetection: number;

    totalImages: number;

    totalVideos: number;

    totalFake: number;

    totalReal: number;

    averageConfidence: number;

    averageProcessingTime: number;

    latestPrediction?: string;

    latestConfidence?: number;

    latestModel?: string;

    latestVersion?: string;

    device?: string;

    todayDetection?: number;

    weekDetection?: number;

    fakePercentage?: number;

    realPercentage?: number;

    imagePercentage?: number;

    videoPercentage?: number;

}

export interface DetectionTrend {

    date: string;

    count: number;

}

export interface PredictionDistribution {

    fake: number;

    real: number;

    image: number;

    video: number;

    fakePercentage: number;

    realPercentage: number;

    imagePercentage: number;

    videoPercentage: number;

}

export interface RecentDetection {

    id: number;

    filename: string;

    fileType: string;

    prediction: string;

    confidence: number;

    riskLevel: string;

    model: string;

    version: string;

    createdAt: string;

}