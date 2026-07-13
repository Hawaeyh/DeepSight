import {
    BrainCircuit,
    CheckCircle2,
    Cpu,
    LoaderCircle,
    ScanFace,
    Sparkles,
} from "lucide-react";

interface Props {
    open: boolean;
}

const STEPS = [
    {
        title: "Uploading Image",
        icon: <Sparkles size={18} />,
    },
    {
        title: "Reading Metadata",
        icon: <Cpu size={18} />,
    },
    {
        title: "Face Detection",
        icon: <ScanFace size={18} />,
    },
    {
        title: "Image Preprocessing",
        icon: <Cpu size={18} />,
    },
    {
        title: "Feature Extraction",
        icon: <BrainCircuit size={18} />,
    },
    {
        title: "Running EfficientNet-B0",
        icon: <BrainCircuit size={18} />,
    },
    {
        title: "Confidence Calculation",
        icon: <Cpu size={18} />,
    },
    {
        title: "Generating AI Report",
        icon: <Sparkles size={18} />,
    },
    {
        title: "Saving Detection",
        icon: <CheckCircle2 size={18} />,
    },
];

export default function LoadingOverlay({
    open,
}: Props) {

    if (!open) {

        return null;

    }

    return (

        <div
            className="
                fixed
                inset-0
                z-[999]
                flex
                items-center
                justify-center
                bg-slate-950/80
                backdrop-blur-md
            "
        >

            <div
                className="
                    w-[520px]
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-slate-900
                    shadow-2xl
                    p-10
                "
            >

                {/* Logo */}

                <div className="flex justify-center">

                    <div
                        className="
                            w-24
                            h-24
                            rounded-full
                            bg-cyan-500/10
                            flex
                            items-center
                            justify-center
                        "
                    >

                        <BrainCircuit
                            size={52}
                            className="text-cyan-400 animate-pulse"
                        />

                    </div>

                </div>

                {/* Title */}

                <h2 className="text-3xl font-bold text-center mt-6">

                    DeepSight AI

                </h2>

                <p className="text-center text-slate-400 mt-2">

                    Initializing Deepfake Detection Engine

                </p>

                {/* Spinner */}

                <div className="flex justify-center mt-6">

                    <LoaderCircle
                        size={34}
                        className="animate-spin text-cyan-400"
                    />

                </div>

                {/* Progress */}

                <div className="mt-8">

                    <div className="flex justify-between text-sm mb-2">

                        <span>

                            AI Processing

                        </span>

                        <span>

                            Please Wait...

                        </span>

                    </div>

                    <div className="w-full h-3 rounded-full bg-slate-700 overflow-hidden">

                        <div
                            className="
                                h-full
                                w-3/4
                                bg-cyan-400
                                animate-pulse
                            "
                        />

                    </div>

                </div>

                {/* AI Steps */}

                <div className="mt-8 space-y-3">

                    {

                        STEPS.map((step) => (

                            <div
                                key={step.title}
                                className="
                                    flex
                                    items-center
                                    gap-3
                                    text-slate-300
                                "
                            >

                                <CheckCircle2
                                    size={18}
                                    className="text-green-400"
                                />

                                {step.icon}

                                <span>

                                    {step.title}

                                </span>

                            </div>

                        ))

                    }

                </div>

                {/* Footer */}

                <div className="mt-8 border-t border-slate-700 pt-5">

                    <p className="text-center text-xs text-slate-500">

                        Powered by DeepSight AI • EfficientNet-B0 • PyTorch

                    </p>

                </div>

            </div>

        </div>

    );

}