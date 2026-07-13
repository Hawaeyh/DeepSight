import Card from "../../../components/ui/Card";

import {

    FolderOpen,

} from "lucide-react";

export default function HistoryEmpty() {

    return (

        <Card>

            <div className="py-20 flex flex-col items-center">

                <FolderOpen

                    size={72}

                    className="text-slate-600"

                />

                <h2 className="mt-6 text-2xl font-bold">

                    No Analysis Found

                </h2>

                <p className="mt-3 text-slate-400">

                    Analyze an image to create your first history record.

                </p>

            </div>

        </Card>

    );

}