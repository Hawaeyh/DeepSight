import {

    BrainCircuit,
    Clock3,
    Download,
    Eye,
    ShieldAlert,
    ShieldCheck,
    Trash2,

} from "lucide-react";

import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import type {

    HistoryItem,

} from "../types/history";

interface Props {

    item: HistoryItem;

    onView: () => void;

    onDownload: () => void;

    onDelete: () => void;

}

export default function HistoryCard({

    item,

    onView,

    onDownload,

    onDelete,

}: Props) {

    const fake = item.prediction === "Fake";

    return (

        <Card>

            <div className="space-y-5">

                <div className="flex justify-between">

                    <div>

                        <h2 className="font-semibold">

                            {item.filename}

                        </h2>

                        <p className="text-sm text-slate-400">

                            {item.model_name}

                        </p>

                    </div>

                    {

                        fake

                        ?

                        <ShieldAlert

                            className="text-red-500"

                        />

                        :

                        <ShieldCheck

                            className="text-green-500"

                        />

                    }

                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">

                    <div>

                        <p className="text-slate-400">

                            Prediction

                        </p>

                        <p>{item.prediction}</p>

                    </div>

                    <div>

                        <p className="text-slate-400">

                            Confidence

                        </p>

                        <p>

                            {item.confidence.toFixed(2)}%

                        </p>

                    </div>

                    <div>

                        <p className="text-slate-400">

                            Risk

                        </p>

                        <p>{item.risk_level}</p>

                    </div>

                    <div>

                        <p className="text-slate-400">

                            Device

                        </p>

                        <p>{item.device.toUpperCase()}</p>

                    </div>

                </div>

                <div className="flex items-center gap-2 text-sm text-slate-400">

                    <Clock3 size={16}/>

                    {new Date(item.created_at).toLocaleString()}

                </div>

                <div className="flex gap-3">

                    <Button

                        onClick={onView}

                    >

                        <Eye size={18}/>

                    </Button>

                    <Button

                        onClick={onDownload}

                    >

                        <Download size={18}/>

                    </Button>

                    <Button

                        variant="danger"

                        onClick={onDelete}

                    >

                        <Trash2 size={18}/>

                    </Button>

                </div>

            </div>

        </Card>

    );

}