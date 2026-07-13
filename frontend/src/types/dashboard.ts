import type {

    Analysis,

} from "./analysis";

export interface DashboardOverview {

    totalDetection: number;

    todayDetection: number;

    weekDetection: number;

    averageConfidence: number;

    realCount: number;

    fakeCount: number;

    device: string;

}

export interface DetectionTrend {

    date: string;

    total: number;

}

export interface PredictionDistribution {

    real: number;

    fake: number;

}

export interface DashboardResponse {

    overview: DashboardOverview;

    trend: DetectionTrend[];

    distribution: PredictionDistribution;

    recent: Analysis[];

}