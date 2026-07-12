import Card from "../../../components/ui/Card";

import type {

    ImageDetectionResponse,

} from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

interface ItemProps {

    label: string;

    value: string;

}

function Item({

    label,

    value,

}: ItemProps) {

    return (

        <div className="flex justify-between items-center py-3 border-b border-slate-700 last:border-b-0">

            <span className="text-slate-400 text-sm">

                {label}

            </span>

            <span className="font-medium text-white text-right">

                {value}

            </span>

        </div>

    );

}

export default function AIInformationCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card

                title="AI Information"

                subtitle="AI inference information"

            >

                <div className="flex flex-col items-center justify-center py-12">

                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-14 h-14 text-slate-600 mb-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >

                        <path

                            strokeLinecap="round"

                            strokeLinejoin="round"

                            strokeWidth={1.5}

                            d="M9.75 17L15 12l-5.25-5"

                        />

                    </svg>

                    <p className="text-slate-400 font-medium">

                        No Detection Available

                    </p>

                    <p className="text-sm text-slate-500 mt-2 text-center">

                        AI information will appear after image analysis.

                    </p>

                </div>

            </Card>

        );

    }

    return (

        <Card

            title="AI Information"

            subtitle="DeepSight AI Inference Details"

        >

            <div className="space-y-1">

                <Item

                    label="Analysis ID"

                    value={`#${result.id}`}

                />

                <Item

                    label="Detection Type"

                    value="Image"

                />

                <Item

                    label="Prediction"

                    value={result.prediction}

                />

                <Item

                    label="Confidence"

                    value={`${result.confidence.toFixed(2)}%`}

                />

                <Item

                    label="Risk Level"

                    value={result.risk_level}

                />

                <Item

                    label="Model"

                    value={result.model_name}

                />

                <Item

                    label="Version"

                    value={result.model_version}

                />

                <Item

                    label="Inference Device"

                    value={result.device.toUpperCase()}

                />

                <Item

                    label="Processing Time"

                    value={`${result.processing_time.toFixed(2)} sec`}

                />

                <Item

                    label="Detection Time"

                    value={new Date(

                        result.created_at

                    ).toLocaleString()}

                />

            </div>

        </Card>

    );

}