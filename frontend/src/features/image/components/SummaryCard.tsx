import Card from "../../../components/ui/Card";
import StatusBadge from "../../../components/ui/StatusBadge";
import Metric from "../../../components/ui/Metric";

import type { ImageDetectionResponse } from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function SummaryCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card

                title="AI Summary"

                subtitle="Prediction overview"

            >

                <p className="text-slate-500">

                    No analysis available.

                </p>

            </Card>

        );

    }

    return (

        <Card

            title="AI Summary"

            subtitle="Binary Detection"

        >

            <div className="space-y-5">

                <div className="flex justify-between items-center">

                    <h2 className="text-3xl font-bold">

                        {result.prediction}

                    </h2>

                    <StatusBadge

                        text={result.risk_level}

                        color={

                            result.risk_level === "High"

                                ? "red"

                                : "green"

                        }

                    />

                </div>

                <Metric

                    label="Confidence"

                    value={`${result.confidence.toFixed(2)} %`}

                />

                <Metric

                    label="Deepfake Type"

                    value={result.deepfake_type ?? "Authentic"}

                />

                <Metric

                    label="Analysis ID"

                    value={result.id}

                />

            </div>

        </Card>

    );

}
