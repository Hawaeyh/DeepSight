import Card from "../../../components/ui/Card";
import ProgressBar from "../../../components/ui/ProgressBar";

import {
    BrainCircuit,
    Clock3,
    Database,
    ShieldAlert,
    ShieldCheck,
    ShieldQuestion,
    Cpu,
    Activity,
} from "lucide-react";

import type { ImageDetectionResponse } from "../types/image";

interface Props {
    result: ImageDetectionResponse | null;
}

interface InfoRowProps {
    label: string;
    value: string | number;
    icon?: React.ReactNode;
}

function InfoRow({
    label,
    value,
    icon,
}: InfoRowProps) {

    return (

        <div className="flex items-center justify-between py-3 border-b border-slate-700 last:border-0">

            <div className="flex items-center gap-2 text-slate-400">

                {icon}

                <span>{label}</span>

            </div>

            <span className="font-semibold text-white">

                {value}

            </span>

        </div>

    );

}

function getConfidenceLevel(confidence: number) {

    if (confidence >= 99) {

        return {
            text: "★★★★★ Excellent",
            color: "text-green-400",
        };

    }

    if (confidence >= 95) {

        return {
            text: "★★★★☆ Very High",
            color: "text-emerald-400",
        };

    }

    if (confidence >= 85) {

        return {
            text: "★★★☆☆ High",
            color: "text-blue-400",
        };

    }

    if (confidence >= 70) {

        return {
            text: "★★☆☆☆ Moderate",
            color: "text-yellow-400",
        };

    }

    return {

        text: "★☆☆☆☆ Low",

        color: "text-red-400",

    };

}

export default function PredictionResultCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card
                title="AI Detection Result"
                subtitle="Prediction will appear here"
            >

                <div className="py-20 text-center text-slate-500">

                    Analyze an image to view the AI prediction.

                </div>

            </Card>

        );

    }

    const isFake = result.prediction === "Fake";

    const confidenceLevel =
        getConfidenceLevel(result.confidence);

    const difference = Math.abs(
        result.real_probability -
        result.fake_probability
    );

    return (

        <Card
            title="AI Detection Result"
            subtitle="DeepSight AI Prediction"
        >

            <div className="space-y-8">

                {/* Prediction */}

                <div className="text-center">

                    <div className="flex justify-center mb-5">

                        {

                            isFake

                                ? (

                                    <ShieldAlert
                                        size={80}
                                        className="text-red-500"
                                    />

                                )

                                : (

                                    <ShieldCheck
                                        size={80}
                                        className="text-green-500"
                                    />

                                )

                        }

                    </div>

                    <h1
                        className={`text-5xl font-black tracking-wide ${
                            isFake
                                ? "text-red-400"
                                : "text-green-400"
                        }`}
                    >

                        {result.prediction.toUpperCase()}

                    </h1>

                    <p className="text-slate-400 mt-2">

                        AI Confidence

                    </p>

                    <h2 className="text-4xl font-bold mt-2">

                        {result.confidence.toFixed(2)}%

                    </h2>

                    <p
                        className={`mt-3 font-semibold ${confidenceLevel.color}`}
                    >

                        {confidenceLevel.text}

                    </p>

                </div>

                {/* Probability */}

                <div className="border-t border-slate-700 pt-6 space-y-5">

                    <h3 className="font-semibold">

                        Probability Distribution

                    </h3>

                    <div>

                        <div className="flex justify-between mb-2">

                            <span>Real Probability</span>

                            <span>

                                {result.real_probability.toFixed(2)}%

                            </span>

                        </div>

                        <ProgressBar
                            value={result.real_probability}
                        />

                    </div>

                    <div>

                        <div className="flex justify-between mb-2">

                            <span>Fake Probability</span>

                            <span>

                                {result.fake_probability.toFixed(2)}%

                            </span>

                        </div>

                        <ProgressBar
                            value={result.fake_probability}
                        />

                    </div>

                    <InfoRow

                        label="Difference"

                        value={`${difference.toFixed(2)}%`}

                        icon={<Activity size={18}/>}

                    />

                </div>

                {/* Details */}

                <div className="border-t border-slate-700 pt-4">

                    <InfoRow
                        label="Risk Level"
                        value={result.risk_level}
                        icon={<ShieldQuestion size={18}/>}
                    />

                    <InfoRow
                        label="Status"
                        value={result.status}
                        icon={<ShieldCheck size={18}/>}
                    />

                    <InfoRow
                        label="Model"
                        value={result.model_name}
                        icon={<BrainCircuit size={18}/>}
                    />

                    <InfoRow
                        label="Version"
                        value={result.model_version}
                        icon={<Cpu size={18}/>}
                    />

                    <InfoRow
                        label="Processing Time"
                        value={`${result.processing_time.toFixed(2)} sec`}
                        icon={<Clock3 size={18}/>}
                    />

                    <InfoRow
                        label="Analysis ID"
                        value={`#${result.id}`}
                        icon={<Database size={18}/>}
                    />

                </div>

                {/* AI Summary */}

                <div className="border-t border-slate-700 pt-6">

                    <h3 className="font-semibold mb-3">

                        AI Decision Summary

                    </h3>

                    <p className="text-sm text-slate-300 leading-7">

                        {

                            result.prediction === "Real"

                                ? `The uploaded image has a significantly higher REAL probability (${result.real_probability.toFixed(2)}%) than FAKE probability (${result.fake_probability.toFixed(2)}%). No obvious manipulation characteristics were detected. The overall confidence of this prediction is ${result.confidence.toFixed(2)}%.`

                                : `The uploaded image has a significantly higher FAKE probability (${result.fake_probability.toFixed(2)}%) than REAL probability (${result.real_probability.toFixed(2)}%). The AI model detected characteristics commonly associated with manipulated or synthetic images. Manual verification is recommended.`

                        }

                    </p>

                </div>

            </div>

        </Card>

    );

}