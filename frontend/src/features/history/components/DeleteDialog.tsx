import Button from "../../../components/ui/Button";
import Card from "../../../components/ui/Card";

import {

    AlertTriangle,

} from "lucide-react";

interface Props {

    open: boolean;

    filename?: string;

    onCancel: () => void;

    onConfirm: () => void;

}

export default function DeleteDialog({

    open,

    filename,

    onCancel,

    onConfirm,

}: Props) {

    if (!open) {

        return null;

    }

    return (

        <div
            className="
                fixed
                inset-0
                z-50
                flex
                items-center
                justify-center
                bg-black/70
                backdrop-blur-sm
            "
        >

            <Card className="w-full max-w-md">

                <div className="flex flex-col items-center">

                    <AlertTriangle

                        size={70}

                        className="text-red-500"

                    />

                    <h2 className="text-2xl font-bold mt-6">

                        Delete Analysis

                    </h2>

                    <p className="text-slate-400 mt-4 text-center">

                        Are you sure you want to delete

                    </p>

                    <p className="font-semibold mt-1">

                        {filename}

                    </p>

                    <p className="text-red-400 mt-5 text-center">

                        This action cannot be undone.

                    </p>

                </div>

                <div className="flex justify-end gap-4 mt-10">

                    <Button

                        variant="secondary"

                        onClick={onCancel}

                    >

                        Cancel

                    </Button>

                    <Button

                        variant="danger"

                        onClick={onConfirm}

                    >

                        Delete

                    </Button>

                </div>

            </Card>

        </div>

    );

}