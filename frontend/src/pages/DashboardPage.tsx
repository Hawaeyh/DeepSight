import DashboardHeader from "../components/dashboard/DashboardHeader";

import KPIGrid from "../components/dashboard/KPIGrid";

import DetectionTrendChart from "../components/dashboard/charts/DetectionTrendChart";
import PredictionDistributionChart from "../components/dashboard/charts/PredictionDistributionChart";

import RecentDetectionTable from "../components/dashboard/RecentDetectionTable";
import AIStatusCard from "../components/dashboard/AIStatusCard";
import CurrentModelCard from "../components/dashboard/CurrentModelCard";
import SystemStatusCard from "../components/dashboard/SystemStatusCard";
import ModelPerformanceCard from "../components/dashboard/ModelPerformanceCard";
import AdminDashboardInsights from "../components/dashboard/AdminDashboardInsights";

import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";

import { useDashboard } from "../hooks/useDashboard";

export default function DashboardPage() {

    const {

        overview,

        trend,

        distribution,

        recent,

        modelMetrics,

        loading,

        error,

    } = useDashboard();

    if (loading) {

        return (

            <div className="flex items-center justify-center h-[70vh]">

                <Spinner />

            </div>

        );

    }

    if (error) {

        return (

            <EmptyState

                title="Dashboard Error"

                description={error}

            />

        );

    }

    if (!overview) {

        return (

            <EmptyState

                title="Dashboard Error"

                description="Overview data is unavailable."

            />

        );

    }

    if (!distribution) {

        return (

            <EmptyState

                title="Dashboard Error"

                description="Prediction distribution is unavailable."

            />

        );

    }

    return (

        <div className="space-y-8">

            <DashboardHeader />

            <KPIGrid

                overview={overview}

            />

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <DetectionTrendChart

                    data={trend}

                />

                <PredictionDistributionChart

                    data={distribution}

                />

            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <RecentDetectionTable

                    data={recent}

                />

                <AIStatusCard

                    device={overview.device ?? "CPU"}

                />

            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <CurrentModelCard

                    model={

                        overview.latestModel ??

                        "EfficientNet-B0"

                    }

                    version={

                        overview.latestVersion ??

                        "Binary V3"

                    }

                />

                <SystemStatusCard />

            </div>

            <ModelPerformanceCard data={modelMetrics} />

            <AdminDashboardInsights models={modelMetrics} />

        </div>

    );

}
