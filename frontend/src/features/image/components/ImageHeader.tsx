import { ImageIcon } from "lucide-react";

export default function ImageHeader() {

    return (

        <div className="flex justify-between items-center">

            <div>

                <div className="flex items-center gap-3">

                    <ImageIcon

                        size={38}

                        className="text-cyan-400"

                    />

                    <h1 className="text-4xl font-bold">

                        Image Detection

                    </h1>

                </div>

                <p className="text-slate-400 mt-2">

                    AI-powered Deepfake Image Detection Platform

                </p>

            </div>

        </div>

    );

}