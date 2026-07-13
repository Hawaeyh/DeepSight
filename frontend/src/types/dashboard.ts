export interface DashboardOverview {
    totalDetection: number;
    totalImages: number;
    totalVideos: number;
    totalFake: number;
    totalReal: number;
    averageConfidence: number;
    averageProcessingTime: number;
    todayDetection: number;
    weekDetection: number;
    latestPrediction: string | null;
    latestConfidence: number | null;
    latestModel: string | null;
    latestVersion: string | null;
    device: string;
    fakePercentage: number;
    realPercentage: number;
    imagePercentage: number;
    videoPercentage: number;
}

export interface DetectionTrend {
    date: string;
    count: number;
}

export interface PredictionDistribution {
    real: number;
    fake: number;
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
    prediction: "Real" | "Fake";
    confidence: number;
    riskLevel: "Low" | "Medium" | "High";
    model: string;
    version: string;
    createdAt: string;
}

export interface DashboardResponse {
    overview: DashboardOverview;
    trend: DetectionTrend[];
    distribution: PredictionDistribution;
    recent: RecentDetection[];
}

export interface ModelMetric {
    model: string;
    usageCount: number;
    usagePercentage: number;
    averageConfidence: number;
    verifiedSamples: number;
    accuracy: number | null;
    precision: number | null;
    recall: number | null;
    f1Score: number | null;
}
