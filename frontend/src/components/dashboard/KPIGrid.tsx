import {

    Activity,

    Image,

    Video,

    ShieldAlert,

    ShieldCheck,

    Brain,

    Timer,

} from "lucide-react";

import KPICard from "./KPICard";

import type {

    DashboardOverview,

} from "../../types/dashboard";

interface Props {

    overview: DashboardOverview;

}

export default function KPIGrid({

    overview,

}: Props) {

    return (

        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">

            <KPICard

                title="Total Detection"

                value={overview.totalDetection}

                subtitle="All analyses"

                icon={Activity}

                color="text-cyan-400"

            />

            <KPICard

                title="Images"

                value={overview.totalImages}

                subtitle={`${overview.imagePercentage ?? 0}%`}

                icon={Image}

                color="text-blue-400"

            />

            <KPICard

                title="Videos"

                value={overview.totalVideos}

                subtitle={`${overview.videoPercentage ?? 0}%`}

                icon={Video}

                color="text-purple-400"

            />

            <KPICard

                title="Fake"

                value={overview.totalFake}

                subtitle={`${overview.fakePercentage ?? 0}%`}

                icon={ShieldAlert}

                color="text-red-400"

            />

            <KPICard

                title="Real"

                value={overview.totalReal}

                subtitle={`${overview.realPercentage ?? 0}%`}

                icon={ShieldCheck}

                color="text-green-400"

            />

            <KPICard

                title="Confidence"

                value={`${overview.averageConfidence.toFixed(2)}%`}

                subtitle="Average"

                icon={Brain}

                color="text-cyan-400"

            />

            <KPICard

                title="Avg Time"

                value={`${overview.averageProcessingTime.toFixed(3)} s`}

                subtitle="Inference"

                icon={Timer}

                color="text-yellow-400"

            />

        </div>

    );

}