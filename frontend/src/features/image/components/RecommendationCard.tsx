import Card from "../../../components/ui/Card";
import type { ImageDetectionResponse } from "../types/image";

interface Props {
    result: ImageDetectionResponse | null;
}

function getAssessment(
    prediction: "Real" | "Fake",
    confidence: number,
) {

    if (prediction === "Real") {

        return {
            title: "Authentic Image",
            risk: "Low",
            recommendation:
                confidence >= 95
                    ? "This image appears authentic and is safe for normal use."
                    : "This image is likely authentic. Manual verification is recommended for critical applications.",
            notes:
                "No obvious deepfake manipulation artefacts were detected.",
        };

    }

    return {
        title: "Possible AI Generated Image",
        risk: confidence >= 95
            ? "High"
            : "Medium",
        recommendation:
            confidence >= 95
                ? "Strong evidence of AI manipulation detected. Do not rely on this image without further verification."
                : "Potential manipulation detected. Further investigation is recommended.",
        notes:
            "Facial inconsistencies or synthetic artefacts may be present.",
    };

}

function RiskBadge({
    risk,
}: {
    risk: string;
}) {

    const color =
        risk === "Low"
            ? "bg-green-500/20 text-green-400"
            : risk === "Medium"
            ? "bg-yellow-500/20 text-yellow-400"
            : "bg-red-500/20 text-red-400";

    return (
        <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${color}`}
        >
            {risk}
        </span>
    );

}

export default function RecommendationCard({
    result,
}: Props) {

    if (!result) {

        return (

            <Card
                title="AI Recommendation"
                subtitle="Decision support"
            >

                <div className="py-12 text-center">

                    <p className="text-slate-400 font-medium">
                        No Recommendation
                    </p>

                    <p className="text-slate-500 mt-2 text-sm">
                        Analyze an image to receive an AI assessment.
                    </p>

                </div>

            </Card>

        );

    }

    const assessment = getAssessment(
        result.prediction,
        result.confidence,
    );

    return (

        <Card
            title="AI Recommendation"
            subtitle="Generated from the prediction result"
        >

            <div className="space-y-6">

                <div>

                    <p className="text-sm text-slate-400">
                        Assessment
                    </p>

                    <h2 className="text-2xl font-bold mt-1">
                        {assessment.title}
                    </h2>

                </div>

                <div>

                    <p className="text-sm text-slate-400 mb-2">
                        Risk Level
                    </p>

                    <RiskBadge
                        risk={assessment.risk}
                    />

                </div>

                <div>

                    <p className="text-sm text-slate-400">
                        Recommendation
                    </p>

                    <p className="mt-2 leading-7">
                        {assessment.recommendation}
                    </p>

                </div>

                <div>

                    <p className="text-sm text-slate-400">
                        Notes
                    </p>

                    <p className="mt-2 leading-7 text-slate-300">
                        {assessment.notes}
                    </p>

                </div>

            </div>

        </Card>

    );

}