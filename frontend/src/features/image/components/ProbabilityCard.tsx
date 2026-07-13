import Card from "../../../components/ui/Card";
import ProgressBar from "../../../components/ui/ProgressBar";
import type {    Analysis, } from "@/types/analysis";

interface Props {
    result: ImageDetectionResponse | null;
}

function getConfidenceLevel(confidence: number) {

    if (confidence >= 99) {

        return {
            label: "Excellent",
            color: "text-green-400 bg-green-500/20",
        };

    }

    if (confidence >= 95) {

        return {
            label: "Very High",
            color: "text-green-400 bg-green-500/20",
        };

    }

    if (confidence >= 85) {

        return {
            label: "High",
            color: "text-blue-400 bg-blue-500/20",
        };

    }

    if (confidence >= 70) {

        return {
            label: "Moderate",
            color: "text-yellow-400 bg-yellow-500/20",
        };

    }

    return {

        label: "Low",

        color: "text-red-400 bg-red-500/20",

    };

}

export default function ProbabilityCard({
    result,
}: Props) {

    if (!result) {

        return (

            <Card
                title="Probability Analysis"
                subtitle="Prediction probability distribution"
            >

                <div className="flex flex-col items-center justify-center py-12">

                    <p className="text-slate-400 font-medium">

                        No Probability Available

                    </p>

                    <p className="text-slate-500 text-sm mt-2">

                        Run an image analysis to view prediction probabilities.

                    </p>

                </div>

            </Card>

        );

    }

    const confidence = getConfidenceLevel(
        result.confidence
    );

    return (

        <Card
            title="Probability Analysis"
            subtitle="AI confidence distribution"
        >

            <div className="space-y-6">

                <div>

                    <div className="flex justify-between mb-2">

                        <span className="font-medium">

                            Real Image

                        </span>

                        <span className="font-semibold">

                            {result.real_probability.toFixed(2)}%

                        </span>

                    </div>

                    <ProgressBar

                        value={result.real_probability}

                    />

                </div>

                <div>

                    <div className="flex justify-between mb-2">

                        <span className="font-medium">

                            Fake Image

                        </span>

                        <span className="font-semibold">

                            {result.fake_probability.toFixed(2)}%

                        </span>

                    </div>

                    <ProgressBar

                        value={result.fake_probability}

                    />

                </div>

                <div className="border-t border-slate-700 pt-5">

                    <div className="flex justify-between items-center">

                        <span className="text-slate-400">

                            Overall Confidence

                        </span>

                        <span className="font-bold text-lg">

                            {result.confidence.toFixed(2)}%

                        </span>

                    </div>

                    <div className="mt-4 flex justify-between items-center">

                        <span className="text-slate-400">

                            Confidence Level

                        </span>

                        <span
                            className={`px-3 py-1 rounded-full text-sm font-semibold ${confidence.color}`}
                        >

                            {confidence.label}

                        </span>

                    </div>

                </div>

            </div>

        </Card>

    );

}