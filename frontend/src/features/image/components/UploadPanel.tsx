import {

    UploadCloud,

} from "lucide-react";

import {

    formatFileSize,

} from "../utils/fileHelper";

interface Props {

    selectedFile: File | null;

    loading: boolean;

    onSelect(

        file: File,

    ): void;

}

export default function UploadPanel({

    selectedFile,

    loading,

    onSelect,

}: Props) {

    function browse(

        e: React.ChangeEvent<HTMLInputElement>

    ) {

        const file =

            e.target.files?.[0];

        if (

            file

        ) {

            onSelect(file);

        }

    }

    return (

        <div

            className="rounded-2xl border border-slate-800 bg-slate-900 p-8"

        >

            <div

                className="border-2 border-dashed border-slate-700 rounded-xl p-10 flex flex-col items-center"

            >

                <UploadCloud

                    className="text-cyan-400"

                    size={60}

                />

                <h2 className="mt-5 text-2xl font-semibold">

                    Upload Image

                </h2>

                <p className="text-slate-400 mt-2">

                    Drag & Drop Image

                </p>

                <p className="text-slate-500">

                    PNG • JPG • JPEG • WEBP

                </p>

                <p className="text-slate-500">

                    Maximum 20 MB

                </p>

                <label

                    className="mt-6 bg-cyan-500 hover:bg-cyan-600 px-6 py-3 rounded-xl cursor-pointer"

                >

                    {

                        loading

                        ?

                        "Uploading..."

                        :

                        "Browse Image"

                    }

                    <input

                        hidden

                        type="file"

                        accept="image/*"

                        onChange={browse}

                    />

                </label>

            </div>

            {

                selectedFile && (

                    <div className="mt-8 space-y-3">

                        <h3 className="font-semibold">

                            Selected File

                        </h3>

                        <div className="flex justify-between">

                            <span>

                                Name

                            </span>

                            <span>

                                {

                                    selectedFile.name

                                }

                            </span>

                        </div>

                        <div className="flex justify-between">

                            <span>

                                Size

                            </span>

                            <span>

                                {

                                    formatFileSize(

                                        selectedFile.size

                                    )

                                }

                            </span>

                        </div>

                        <div className="flex justify-between">

                            <span>

                                Type

                            </span>

                            <span>

                                {

                                    selectedFile.type

                                }

                            </span>

                        </div>

                    </div>

                )

            }

        </div>

    );

}