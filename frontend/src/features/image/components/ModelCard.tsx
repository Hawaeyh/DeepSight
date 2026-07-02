import Card from "../../../components/ui/Card";
import Metric from "../../../components/ui/Metric";

import type { ImageDetectionResponse } from "../../../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function ModelCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="AI Model">

                <p className="text-slate-500">

                    No model information.

                </p>

            </Card>

        );

    }

    return (

        <Card

            title="AI Model"

            subtitle="Detection Engine"

        >

            <div className="space-y-4">

                <Metric

                    label="Model"

                    value={result.model.name}

                />

                <Metric

                    label="Version"

                    value={result.model.version}

                />

                <Metric

                    label="Device"

                    value={result.model.device.toUpperCase()}

                />

                <Metric

                    label="Processing"

                    value={`${result.processing.time.toFixed(2)} sec`}

                />

            </div>

        </Card>

    );

}