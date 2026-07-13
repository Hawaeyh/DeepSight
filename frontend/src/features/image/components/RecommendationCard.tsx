import Card from "../../../components/ui/Card";

import {
    CheckCircle2,
    AlertTriangle,
    ShieldCheck,
    ShieldAlert,
    Info,
} from "lucide-react";

import type { ImageDetectionResponse } from "../types/image";

interface Props {
    result: ImageDetectionResponse | null;
}

interface Recommendation {

    title: string;

    icon: React.ReactNode;

    color: string;

    assessment: string;

    recommendation: string;

    notes: string[];

}

function buildRecommendation(
    result: ImageDetectionResponse,
): Recommendation {

    const isReal = result.prediction === "Real";

    if (isReal) {

        return {

            title: "Authentic Image",

            icon: <ShieldCheck size={56} className="text-green-500" />,

            color: "text-green-400",

            assessment:
                "The AI model predicts that this image is authentic.",

            recommendation:
                "This image appears safe for normal viewing, sharing and business use.",

            notes: [

                `Real Probability: ${result.real_probability.toFixed(2)}%`,

                `Fake Probability: ${result.fake_probability.toFixed(2)}%`,

                "No obvious manipulation characteristics detected.",

                "Manual verification is optional.",

            ],

        };

    }

    return {

        title: "Potential Deepfake",

        icon: <ShieldAlert size={56} className="text-red-500" />,

        color: "text-red-400",

        assessment:
            "The AI model detected characteristics commonly associated with manipulated images.",

        recommendation:
            "Do not fully trust this image until manual verification has been performed.",

        notes: [

            `Fake Probability: ${result.fake_probability.toFixed(2)}%`,

            `Real Probability: ${result.real_probability.toFixed(2)}%`,

            "Possible AI-generated or manipulated facial features.",

            "Human verification is highly recommended.",

        ],

    };

}

export default function RecommendationCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card
                title="AI Recommendation"
                subtitle="Generated after AI analysis"
            >

                <div className="py-14 text-center text-slate-500">

                    Analyze an image to receive an AI recommendation.

                </div>

            </Card>

        );

    }

    const recommendation =
        buildRecommendation(result);

    return (

        <Card
            title="AI Recommendation"
            subtitle="Generated from AI prediction"
        >

            <div className="space-y-8">

                {/* Header */}

                <div className="text-center">

                    <div className="flex justify-center mb-4">

                        {recommendation.icon}

                    </div>

                    <h2
                        className={`text-3xl font-bold ${recommendation.color}`}
                    >

                        {recommendation.title}

                    </h2>

                </div>

                {/* Assessment */}

                <section>

                    <h3 className="font-semibold mb-3 flex items-center gap-2">

                        <Info size={18} />

                        Assessment

                    </h3>

                    <p className="text-slate-300 leading-7">

                        {recommendation.assessment}

                    </p>

                </section>

                {/* Recommendation */}

                <section>

                    <h3 className="font-semibold mb-3 flex items-center gap-2">

                        <CheckCircle2 size={18} />

                        Recommendation

                    </h3>

                    <p className="text-slate-300 leading-7">

                        {recommendation.recommendation}

                    </p>

                </section>

                {/* Notes */}

                <section>

                    <h3 className="font-semibold mb-4 flex items-center gap-2">

                        <AlertTriangle size={18} />

                        AI Notes

                    </h3>

                    <ul className="space-y-3">

                        {

                            recommendation.notes.map(

                                (note, index) => (

                                    <li
                                        key={index}
                                        className="flex items-start gap-3 text-slate-300"
                                    >

                                        <CheckCircle2
                                            size={18}
                                            className="text-green-400 mt-1"
                                        />

                                        <span>

                                            {note}

                                        </span>

                                    </li>

                                ),

                            )

                        }

                    </ul>

                </section>

            </div>

        </Card>

    );

}