import Card from "../../../components/ui/Card";

import type {

    ImageDetectionResponse,

} from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function ResultCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="Detection Result">

                <p className="text-slate-500">

                    No analysis available.

                </p>

            </Card>

        );

    }

    return (

        <Card title="Detection Result">

            <div className="space-y-5">

                <div>

                    <p className="text-slate-400">

                        Prediction

                    </p>

                    <h2 className="text-4xl font-bold">

                        {result.prediction.label}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Confidence

                    </p>

                    <h3 className="text-2xl">

                        {result.prediction.confidence.toFixed(2)}%

                    </h3>

                </div>

                <div>

                    <p className="text-slate-400">

                        Risk Level

                    </p>

                    <span

                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                            result.prediction.riskLevel === "High"
                                ? "bg-red-500/20 text-red-400"
                                : "bg-green-500/20 text-green-400"
                        }`}

                    >

                        {result.prediction.riskLevel}

                    </span>

                </div>

                <div>

                    <p className="text-slate-400">

                        Deepfake Type

                    </p>

                    <h3>

                        {result.deepfake.type ?? "Authentic"}

                    </h3>

                </div>

            </div>

        </Card>

    );

}