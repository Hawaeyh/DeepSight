import Button from "../../../components/ui/Button";
import Card from "../../../components/ui/Card";
import Spinner from "../../../components/ui/Spinner";

import {
    Eye,
    Download,
    Trash2,
    ShieldCheck,
    ShieldAlert,
} from "lucide-react";

import type { HistoryItem } from "../types/history";

interface Props {

    loading: boolean;

    history: HistoryItem[];

    onView: (item: HistoryItem) => void;

    onDownload: (id: number) => void;

    onDelete: (id: number) => void;

}

export default function HistoryTable({

    loading,

    history,

    onView,

    onDownload,

    onDelete,

}: Props) {

    if (loading) {

        return (

            <Card title="Detection History">

                <div className="py-16">

                    <Spinner />

                </div>

            </Card>

        );

    }

    if (history.length === 0) {

        return (

            <Card title="Detection History">

                <div className="py-16 text-center">

                    <h2 className="text-xl font-semibold">

                        No Detection History

                    </h2>

                    <p className="text-slate-400 mt-3">

                        Analyze an image to create your first history record.

                    </p>

                </div>

            </Card>

        );

    }

    return (

        <Card

            title="Detection History"

            subtitle={`${history.length} record(s)`}

        >

            <div className="overflow-x-auto">

                <table className="w-full">

                    <thead>

                        <tr className="border-b border-slate-700">

                            <th className="py-4 text-left">

                                Filename

                            </th>

                            <th className="text-left">

                                Prediction

                            </th>

                            <th className="text-left">

                                Confidence

                            </th>

                            <th className="text-left">

                                Risk

                            </th>

                            <th className="text-left">

                                Model

                            </th>

                            <th className="text-left">

                                Date

                            </th>

                            <th className="text-center">

                                Actions

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {

                            history.map(item => (

                                <tr

                                    key={item.id}

                                    className="

                                        border-b

                                        border-slate-800

                                        hover:bg-slate-800/40

                                        transition

                                    "

                                >

                                    <td className="py-5">

                                        <div>

                                            <h3 className="font-semibold">

                                                {item.filename}

                                            </h3>

                                            <p className="text-sm text-slate-400">

                                                {item.file_extension}

                                            </p>

                                        </div>

                                    </td>

                                    <td>

                                        <div className="flex items-center gap-2">

                                            {

                                                item.prediction === "Real"

                                                ?

                                                <ShieldCheck

                                                    size={18}

                                                    className="text-green-500"

                                                />

                                                :

                                                <ShieldAlert

                                                    size={18}

                                                    className="text-red-500"

                                                />

                                            }

                                            {item.prediction}

                                        </div>

                                    </td>

                                    <td>

                                        {item.confidence.toFixed(2)}%

                                    </td>

                                    <td>

                                        <span

                                            className={`

                                                px-3

                                                py-1

                                                rounded-full

                                                text-sm

                                                ${

                                                    item.risk_level === "Low"

                                                        ? "bg-green-500/20 text-green-400"

                                                    : item.risk_level === "Medium"

                                                        ? "bg-yellow-500/20 text-yellow-400"

                                                        : "bg-red-500/20 text-red-400"

                                                }

                                            `}

                                        >

                                            {item.risk_level}

                                        </span>

                                    </td>

                                    <td>

                                        <div>

                                            <h3>

                                                {item.model_name}

                                            </h3>

                                            <p className="text-sm text-slate-400">

                                                {item.model_version}

                                            </p>

                                        </div>

                                    </td>

                                    <td>

                                        {new Date(

                                            item.created_at,

                                        ).toLocaleString()}

                                    </td>

                                    <td>

                                        <div className="flex justify-center gap-2">

                                            <Button

                                                onClick={() =>

                                                    onView(item)

                                                }

                                                className="px-3 py-2"

                                            >

                                                <Eye size={18} />

                                            </Button>

                                            <Button

                                                onClick={() =>

                                                    onDownload(item.id)

                                                }

                                                className="

                                                    bg-green-600

                                                    hover:bg-green-500

                                                    px-3

                                                    py-2

                                                "

                                            >

                                                <Download size={18} />

                                            </Button>

                                            <Button

                                                onClick={() =>

                                                    onDelete(item.id)

                                                }

                                                className="

                                                    bg-red-600

                                                    hover:bg-red-500

                                                    px-3

                                                    py-2

                                                "

                                            >

                                                <Trash2 size={18} />

                                            </Button>

                                        </div>

                                    </td>

                                </tr>

                            ))

                        }

                    </tbody>

                </table>

            </div>

        </Card>

    );

}