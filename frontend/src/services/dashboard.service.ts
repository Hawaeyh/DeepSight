import api from "./api";

export async function getDashboardOverview() {

    const response = await api.get(

        "/dashboard/overview"

    );

    return response.data;

}

export async function getDetectionTrend() {

    const response = await api.get(

        "/dashboard/trend"

    );

    return response.data;

}

export async function getPredictionDistribution() {

    const response = await api.get(

        "/dashboard/distribution"

    );

    return response.data;

}

export async function getRecentDetection() {

    const response = await api.get(

        "/dashboard/recent"

    );

    return response.data;

}

export async function getModelMetrics() {
    const response = await api.get("/dashboard/models");
    return response.data;
}
