import Card from "../../../components/ui/Card";
import ProgressBar from "../../../components/ui/ProgressBar";

import {

    ShieldCheck,

    ShieldAlert,

    BrainCircuit,

    Clock3,

    Database,

} from "lucide-react";

import type {

    ImageDetectionResponse,

} from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

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

                    Analyze an image to view the result.

                </div>

            </Card>

        );

    }

    const isFake =

        result.prediction === "Fake";

    return (

        <Card

            title="AI Detection Result"

            subtitle="EfficientNet Prediction"

        >

            <div className="space-y-6">

                <div className="flex justify-center">

                    {

                        isFake ?

                        (

                            <ShieldAlert

                                size={72}

                                className="text-red-500"

                            />

                        )

                        :

                        (

                            <ShieldCheck

                                size={72}

                                className="text-green-500"

                            />

                        )

                    }

                </div>

                <div className="text-center">

                    <h1

                        className={`

                        text-4xl

                        font-bold

                        ${

                            isFake

                            ?

                            "text-red-400"

                            :

                            "text-green-400"

                        }

                        `}

                    >

                        {result.prediction.toUpperCase()}

                    </h1>

                </div>

                <div>

                    <div className="flex justify-between mb-2">

                        <span>

                            Confidence

                        </span>

                        <span>

                            {result.confidence.toFixed(2)}%

                        </span>

                    </div>

                    <ProgressBar

                        value={result.confidence}

                    />

                </div>

                <div className="space-y-4">

                    <InfoRow

                        label="Risk"

                        value={result.riskLevel}

                    />

                    <InfoRow

                        label="Recommendation"

                        value={result.recommendation}

                    />

                    <InfoRow

                        label="Model"

                        value={result.model}

                        icon={<BrainCircuit size={18}/>}

                    />

                    <InfoRow

                        label="Version"

                        value={result.version}

                    />

                    <InfoRow

                        label="Processing"

                        value={`${result.processingTime} sec`}

                        icon={<Clock3 size={18}/>}

                    />

                    <InfoRow

                        label="Analysis ID"

                        value={`#${result.analysisId}`}

                        icon={<Database size={18}/>}

                    />

                </div>

            </div>

        </Card>

    );

}

interface RowProps{

    label:string;

    value:string|number;

    icon?:React.ReactNode;

}

function InfoRow({

    label,

    value,

    icon,

}:RowProps){

    return(

        <div

            className="

            flex

            justify-between

            items-center

            border-b

            border-slate-800

            pb-3

            "

        >

            <div className="flex items-center gap-2">

                {icon}

                <span>

                    {label}

                </span>

            </div>

            <span

                className="font-semibold"

            >

                {value}

            </span>

        </div>

    );

}