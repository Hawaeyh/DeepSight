import { useCallback, useEffect, useRef, useState } from "react";

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
import { useAuth } from "./useAuth";

type DashboardPayload = [DashboardOverview, DetectionTrend[], PredictionDistribution, RecentDetection[], ModelMetric[]];
let dashboardRequest: Promise<DashboardPayload> | null = null;

function fetchDashboard(): Promise<DashboardPayload> {
    if (!dashboardRequest) {
        dashboardRequest = Promise.all([
            getDashboardOverview(), getDetectionTrend(), getPredictionDistribution(), getRecentDetection(), getModelMetrics(),
        ]).finally(() => { dashboardRequest = null; }) as Promise<DashboardPayload>;
    }
    return dashboardRequest;
}

export function useDashboard() {

    const { authStatus } = useAuth();
    const authStatusRef = useRef(authStatus);
    authStatusRef.current = authStatus;

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

        if (authStatus !== "authenticated") {
            setLoading(authStatus === "loading");
            return;
        }
        try {

            setLoading(true);

            setError(null);

            const [

                overviewData,

                trendData,

                distributionData,

                recentData,

                modelMetricsData,

            ] = await fetchDashboard();

            if (authStatusRef.current !== "authenticated") return;

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

    }, [authStatus]);

    useEffect(() => {

        if (authStatus !== "authenticated") {
            setOverview(null); setTrend([]); setDistribution(null); setRecent([]); setModelMetrics([]); setError(null);
            setLoading(authStatus === "loading");
            return;
        }
        loadDashboard();

        const interval = setInterval(() => {

            loadDashboard();

        }, 15000);

        return () => clearInterval(interval);

    }, [authStatus, loadDashboard]);

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
