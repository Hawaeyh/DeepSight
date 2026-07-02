import {

    LoaderCircle,

} from "lucide-react";

interface Props {

    open: boolean;

}

export default function LoadingOverlay({

    open,

}: Props) {

    if (!open) return null;

    return (

        <div
            className="
                fixed
                inset-0
                bg-black/70
                backdrop-blur-sm
                z-50
                flex
                items-center
                justify-center
            "
        >

            <div
                className="
                    bg-slate-900
                    rounded-2xl
                    p-10
                    w-[420px]
                    border
                    border-slate-700
                "
            >

                <LoaderCircle

                    size={60}

                    className="
                        animate-spin
                        text-cyan-400
                        mx-auto
                    "

                />

                <h2 className="text-2xl font-bold mt-6 text-center">

                    AI Processing

                </h2>

                <p className="text-center text-slate-400 mt-3">

                    Detecting Deepfake...

                </p>

                <div className="mt-8 space-y-3 text-sm">

                    <p>

                        ✔ Loading AI Model

                    </p>

                    <p>

                        ✔ Extracting Features

                    </p>

                    <p>

                        ✔ Running Binary Classifier

                    </p>

                    <p>

                        ✔ Generating Prediction

                    </p>

                </div>

            </div>

        </div>

    );

}