import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";

import {
    ShieldCheck,
    ShieldAlert,
    Cpu,
    Clock3,
    Image,
    ScanFace,
    Download,
    X,
} from "lucide-react";

import type { HistoryItem } from "../types/history";

interface Props {

    open: boolean;

    item: HistoryItem | null;

    onClose: () => void;

    onDownload: () => void;

}

interface RowProps {

    label: string;

    value: string | number;

}

function InfoRow({

    label,

    value,

}: RowProps) {

    return (

        <div className="flex justify-between py-3 border-b border-slate-800">

            <span className="text-slate-400">

                {label}

            </span>

            <span className="font-semibold">

                {value}

            </span>

        </div>

    );

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

                z-50

                bg-black/70

                backdrop-blur-sm

                flex

                justify-center

                items-center

                p-6

            "

        >

            <div className="w-full max-w-5xl">

                <Card

                    title="Detection Detail"

                    subtitle="DeepSight AI Analysis"

                    action={

                        <button

                            onClick={onClose}

                        >

                            <X size={24} />

                        </button>

                    }

                >

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                        {/* Prediction */}

                        <div>

                            <h3 className="text-xl font-semibold mb-6">

                                AI Prediction

                            </h3>

                            <div className="flex justify-center mb-8">

                                {

                                    item.prediction === "Real"

                                        ?

                                        <ShieldCheck

                                            size={80}

                                            className="text-green-500"

                                        />

                                        :

                                        <ShieldAlert

                                            size={80}

                                            className="text-red-500"

                                        />

                                }

                            </div>

                            <InfoRow

                                label="Prediction"

                                value={item.prediction}

                            />

                            <InfoRow

                                label="Confidence"

                                value={`${item.confidence.toFixed(2)} %`}

                            />

                            <InfoRow

                                label="Real Probability"

                                value={`${item.real_probability.toFixed(2)} %`}

                            />

                            <InfoRow

                                label="Fake Probability"

                                value={`${item.fake_probability.toFixed(2)} %`}

                            />

                            <InfoRow

                                label="Risk"

                                value={item.risk_level}

                            />

                        </div>

                        {/* Metadata */}

                        <div>

                            <h3 className="text-xl font-semibold mb-6">

                                Analysis Information

                            </h3>

                            <InfoRow

                                label="Filename"

                                value={item.filename}

                            />

                            <InfoRow

                                label="Extension"

                                value={item.file_extension}

                            />

                            <InfoRow

                                label="Resolution"

                                value={`${item.image_width} × ${item.image_height}`}

                            />

                            <InfoRow

                                label="Face Detected"

                                value={

                                    item.face_detected

                                        ? "Yes"

                                        : "No"

                                }

                            />

                            <InfoRow

                                label="Face Count"

                                value={item.face_count}

                            />

                            <InfoRow

                                label="Status"

                                value={item.status}

                            />

                        </div>

                    </div>

                    {/* Model */}

                    <div className="mt-10">

                        <h3 className="text-xl font-semibold mb-5">

                            AI Model

                        </h3>

                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">

                            <MiniCard

                                icon={<Cpu size={26}/>}

                                title="Model"

                                value={item.model_name}

                            />

                            <MiniCard

                                icon={<Image size={26}/>}

                                title="Version"

                                value={item.model_version}

                            />

                            <MiniCard

                                icon={<Clock3 size={26}/>}

                                title="Processing"

                                value={`${item.processing_time.toFixed(2)} sec`}

                            />

                            <MiniCard

                                icon={<ScanFace size={26}/>}

                                title="Device"

                                value={item.device.toUpperCase()}

                            />

                        </div>

                    </div>

                    <div className="flex justify-end gap-4 mt-10">

                        <Button

                            className="bg-slate-700 hover:bg-slate-600"

                            onClick={onClose}

                        >

                            Close

                        </Button>

                        <Button

                            className="flex items-center gap-2"

                            onClick={onDownload}

                        >

                            <Download size={18}/>

                            Download Report

                        </Button>

                    </div>

                </Card>

            </div>

        </div>

    );

}

interface MiniCardProps {

    icon: React.ReactNode;

    title: string;

    value: string;

}

function MiniCard({

    icon,

    title,

    value,

}: MiniCardProps) {

    return (

        <div

            className="

                rounded-xl

                border

                border-slate-700

                bg-slate-800

                p-5

            "

        >

            <div className="text-cyan-400">

                {icon}

            </div>

            <p className="text-slate-400 mt-3">

                {title}

            </p>

            <h4 className="font-semibold mt-2">

                {value}

            </h4>

        </div>

    );

}