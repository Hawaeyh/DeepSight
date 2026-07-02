import Card from "../../../components/ui/Card";
import StatusBadge from "../../../components/ui/StatusBadge";
import Metric from "../../../components/ui/Metric";

import type { ImageDetectionResponse } from "../../../types/image";

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

                        {result.prediction.label}

                    </h2>

                    <StatusBadge

                        text={result.prediction.riskLevel}

                        color={

                            result.prediction.riskLevel === "High"

                                ? "red"

                                : "green"

                        }

                    />

                </div>

                <Metric

                    label="Confidence"

                    value={`${result.prediction.confidence.toFixed(2)} %`}

                />

                <Metric

                    label="Deepfake Type"

                    value={result.deepfake.type}

                />

                <Metric

                    label="Analysis ID"

                    value={result.analysisId}

                />

            </div>

        </Card>

    );

}