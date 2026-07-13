import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import type {

    HistoryItem,

} from "../types/history";

interface Props {

    open: boolean;

    item: HistoryItem | null;

    onClose: () => void;

    onDownload: () => void;

}

export default function HistoryDetailModal({

    open,

    item,

    onClose,

    onDownload,

}: Props) {

    if (!open || !item) {

        return null;

    }

    return (

        <div
            className="
                fixed
                inset-0
                bg-black/70
                backdrop-blur-sm
                flex
                items-center
                justify-center
                z-50
            "
        >

            <Card
                className="w-full max-w-2xl"
                title="Analysis Detail"
            >

                <div className="grid grid-cols-2 gap-6">

                    <Info label="Filename" value={item.filename} />

                    <Info label="Prediction" value={item.prediction} />

                    <Info
                        label="Confidence"
                        value={`${item.confidence.toFixed(2)}%`}
                    />

                    <Info
                        label="Real Probability"
                        value={`${item.real_probability.toFixed(2)}%`}
                    />

                    <Info
                        label="Fake Probability"
                        value={`${item.fake_probability.toFixed(2)}%`}
                    />

                    <Info
                        label="Risk"
                        value={item.risk_level}
                    />

                    <Info
                        label="Model"
                        value={item.model_name}
                    />

                    <Info
                        label="Version"
                        value={item.model_version}
                    />

                    <Info
                        label="Device"
                        value={item.device.toUpperCase()}
                    />

                    <Info
                        label="Processing"
                        value={`${item.processing_time.toFixed(2)} sec`}
                    />

                    <Info
                        label="Status"
                        value={item.status}
                    />

                    <Info
                        label="Created"
                        value={new Date(item.created_at).toLocaleString()}
                    />

                </div>

                <div className="flex justify-end gap-3 mt-8">

                    <Button
                        onClick={onDownload}
                    >
                        Download Report
                    </Button>

                    <Button
                        variant="secondary"
                        onClick={onClose}
                    >
                        Close
                    </Button>

                </div>

            </Card>

        </div>

    );

}

interface InfoProps {

    label: string;

    value: string;

}

function Info({

    label,

    value,

}: InfoProps) {

    return (

        <div>

            <p className="text-sm text-slate-400">

                {label}

            </p>

            <p className="font-semibold mt-1">

                {value}

            </p>

        </div>

    );

}