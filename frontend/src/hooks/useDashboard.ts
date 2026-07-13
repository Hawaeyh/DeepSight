import { useCallback, useEffect, useState } from "react";

import {
    getDashboardOverview,
    getDetectionTrend,
    getPredictionDistribution,
    getRecentDetection,
    getModelMetrics,
} from "../services/dashboard.service";

import type {
    DashboardOverview,
    DetectionTrend,
    PredictionDistribution,
    RecentDetection,
    ModelMetric,
} from "../types/dashboard";

export function useDashboard() {

    const [overview, setOverview] =
        useState<DashboardOverview | null>(null);

    const [trend, setTrend] =
        useState<DetectionTrend[]>([]);

    const [distribution, setDistribution] =
        useState<PredictionDistribution | null>(null);

    const [recent, setRecent] =
        useState<RecentDetection[]>([]);

    const [modelMetrics, setModelMetrics] =
        useState<ModelMetric[]>([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    const loadDashboard = useCallback(async () => {

        try {

            setLoading(true);

            setError(null);

            const [

                overviewData,

                trendData,

                distributionData,

                recentData,

                modelMetricsData,

            ] = await Promise.all([

                getDashboardOverview(),

                getDetectionTrend(),

                getPredictionDistribution(),

                getRecentDetection(),

                getModelMetrics(),

            ]);

            console.log("Overview:", overviewData);
            console.log("Trend:", trendData);
            console.log("Distribution:", distributionData);
            console.log("Recent:", recentData);

            setOverview(overviewData);

            setTrend(trendData);

            setDistribution(distributionData);

            setRecent(recentData);

            setModelMetrics(modelMetricsData);

        }

        catch (err: any) {

            console.error(err);

            setError(

                err?.response?.data?.detail ||

                err?.message ||

                "Failed to load dashboard."

            );

        }

        finally {

            setLoading(false);

        }

    }, []);

    useEffect(() => {

        loadDashboard();

        const interval = setInterval(() => {

            loadDashboard();

        }, 15000);

        return () => clearInterval(interval);

    }, [loadDashboard]);

    return {

        overview,

        trend,

        distribution,

        recent,

        modelMetrics,

        loading,

        error,

        refresh: loadDashboard,

    };

}
