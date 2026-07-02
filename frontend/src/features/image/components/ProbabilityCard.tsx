import Card from "../../../components/ui/Card";
import ProgressBar from "../../../components/ui/ProgressBar";

import type { ImageDetectionResponse } from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function ProbabilityCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="Probability">

                <p className="text-slate-500">

                    No probability available.

                </p>

            </Card>

        );

    }

    return (

        <Card title="Probability">

            <div className="space-y-6">

                <div>

                    <div className="flex justify-between mb-2">

                        <span>Real</span>

                        <span>

                            {result.probabilities.real.toFixed(2)}%

                        </span>

                    </div>

                    <ProgressBar

                        value={result.probabilities.real}

                    />

                </div>

                <div>

                    <div className="flex justify-between mb-2">

                        <span>Fake</span>

                        <span>

                            {result.probabilities.fake.toFixed(2)}%

                        </span>

                    </div>

                    <ProgressBar

                        value={result.probabilities.fake}

                    />

                </div>

            </div>

        </Card>

    );

}