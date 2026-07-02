import { useDropzone } from "react-dropzone";

import {

    UploadCloud,

    CheckCircle2,

    ImageIcon,

} from "lucide-react";

import Card from "../../../components/ui/Card";

interface Props {

    selectedFile: File | null;

    loading: boolean;

    onSelect(file: File): void;

}

export default function UploadCard({

    selectedFile,

    loading,

    onSelect,

}: Props) {

    const {

        getRootProps,

        getInputProps,

        isDragActive,

    } = useDropzone({

        accept: {

            "image/png": [],

            "image/jpeg": [],

            "image/webp": [],

        },

        multiple: false,

        onDrop: (files) => {

            if (files.length > 0) {

                onSelect(files[0]);

            }

        },

    });

    return (

        <Card

            title="Upload Image"

            subtitle="AI Deepfake Detection"

        >

            <div

                {...getRootProps()}

                className={`

                    cursor-pointer

                    rounded-2xl

                    border-2

                    border-dashed

                    transition-all

                    duration-300

                    p-10

                    text-center

                    ${

                        isDragActive

                            ? "border-cyan-400 bg-cyan-500/10"

                            : "border-slate-700 hover:border-cyan-500"

                    }

                `}

            >

                <input

                    {...getInputProps()}

                />

                {

                    selectedFile ? (

                        <>

                            <CheckCircle2

                                size={70}

                                className="mx-auto text-green-400"

                            />

                            <h2 className="mt-6 text-xl font-semibold">

                                {selectedFile.name}

                            </h2>

                            <p className="text-slate-400 mt-2">

                                Ready for analysis

                            </p>

                            <div className="mt-6 text-sm text-slate-400">

                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB

                            </div>

                        </>

                    ) : (

                        <>

                            <UploadCloud

                                size={70}

                                className="mx-auto text-cyan-400"

                            />

                            <h2 className="mt-6 text-2xl font-bold">

                                Drag & Drop Image

                            </h2>

                            <p className="text-slate-400 mt-3">

                                or click to browse

                            </p>

                            <div className="mt-8 flex justify-center gap-3 flex-wrap">

                                <span className="px-3 py-1 rounded-full bg-slate-800">

                                    PNG

                                </span>

                                <span className="px-3 py-1 rounded-full bg-slate-800">

                                    JPG

                                </span>

                                <span className="px-3 py-1 rounded-full bg-slate-800">

                                    JPEG

                                </span>

                                <span className="px-3 py-1 rounded-full bg-slate-800">

                                    WEBP

                                </span>

                            </div>

                            <div className="mt-6 text-sm text-slate-500">

                                Maximum upload size: 20 MB

                            </div>

                        </>

                    )

                }

            </div>

            <div className="mt-6 flex justify-between items-center">

                <div className="flex items-center gap-2">

                    <ImageIcon

                        size={18}

                        className="text-cyan-400"

                    />

                    <span className="text-sm text-slate-400">

                        Status

                    </span>

                </div>

                <span

                    className={`

                        text-sm

                        font-medium

                        ${

                            selectedFile

                                ? "text-green-400"

                                : "text-yellow-400"

                        }

                    `}

                >

                    {

                        selectedFile

                            ? "Ready"

                            : "Waiting"

                    }

                </span>

            </div>

            {

                loading && (

                    <div className="mt-5">

                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">

                            <div className="h-full w-full animate-pulse bg-cyan-500" />

                        </div>

                    </div>

                )

            }

        </Card>

    );

}