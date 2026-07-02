import Card from "../../../components/ui/Card";

import {

    CheckCircle2,

    LoaderCircle,

    Circle,

} from "lucide-react";

interface Props {

    loading: boolean;

    finished: boolean;

}

const steps = [

    "Image Uploaded",

    "Image Validation",

    "Face Detection",

    "Image Preprocessing",

    "Feature Extraction",

    "Binary Classification",

    "Confidence Calculation",

    "Generate Recommendation",

    "Save Detection",

];

export default function DetectionPipeline({

    loading,

    finished,

}: Props) {

    return (

        <Card

            title="Detection Pipeline"

            subtitle="AI Processing"

        >

            <div className="space-y-5">

                {

                    steps.map((step) => (

                        <div

                            key={step}

                            className="flex items-center gap-4"

                        >

                            {

                                finished ? (

                                    <CheckCircle2

                                        size={20}

                                        className="text-green-500"

                                    />

                                ) : loading ? (

                                    <LoaderCircle

                                        size={20}

                                        className="animate-spin text-cyan-400"

                                    />

                                ) : (

                                    <Circle

                                        size={20}

                                        className="text-slate-600"

                                    />

                                )

                            }

                            <span>

                                {step}

                            </span>

                        </div>

                    ))

                }

            </div>

        </Card>

    );

}