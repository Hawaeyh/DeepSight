import Card from "../../../components/ui/Card";

import {
    BrainCircuit,
    CalendarClock,
    CheckCircle2,
    Clock3,
    Cpu,
    Database,
    ShieldCheck,
} from "lucide-react";

import type { ImageDetectionResponse } from "../types/image";

interface Props {
    result: ImageDetectionResponse | null;
}

interface InfoRowProps {
    icon: React.ReactNode;
    label: string;
    value: string;
}

function InfoRow({
    icon,
    label,
    value,
}: InfoRowProps) {

    return (

        <div className="flex items-center justify-between py-3 border-b border-slate-700 last:border-0">

            <div className="flex items-center gap-2 text-slate-400">

                {icon}

                <span>{label}</span>

            </div>

            <span className="font-semibold text-white">

                {value}

            </span>

        </div>

    );

}

export default function AIInformationCard({
    result,
}: Props) {

    if (!result) {

        return (

            <Card
                title="AI Information"
                subtitle="DeepSight AI Inference"
            >

                <div className="py-16 text-center text-slate-500">

                    Analyze an image to display AI inference information.

                </div>

            </Card>

        );

    }

    return (

        <Card
            title="AI Information"
            subtitle="DeepSight AI Inference"
        >

            <div className="space-y-6">

                {/* Header */}

                <div className="text-center">

                    <BrainCircuit
                        size={60}
                        className="mx-auto text-cyan-400"
                    />

                    <h2 className="text-2xl font-bold mt-4">

                        DeepSight AI

                    </h2>

                    <p className="text-slate-400 mt-2">

                        Binary Deepfake Detection

                    </p>

                </div>

                {/* Information */}

                <div className="border-t border-slate-700 pt-4">

                    <InfoRow
                        icon={<Database size={18}/>}
                        label="Analysis ID"
                        value={`#${result.id}`}
                    />

                    <InfoRow
                        icon={<ShieldCheck size={18}/>}
                        label="Prediction"
                        value={result.prediction}
                    />

                    <InfoRow
                        icon={<Cpu size={18}/>}
                        label="Inference Device"
                        value={result.device.toUpperCase()}
                    />

                    <InfoRow
                        icon={<BrainCircuit size={18}/>}
                        label="Model"
                        value={result.model_name}
                    />

                    <InfoRow
                        icon={<Database size={18}/>}
                        label="Model Version"
                        value={result.model_version}
                    />

                    <InfoRow
                        icon={<Clock3 size={18}/>}
                        label="Processing Time"
                        value={`${result.processing_time.toFixed(2)} sec`}
                    />

                    <InfoRow
                        icon={<CheckCircle2 size={18}/>}
                        label="Status"
                        value={result.status}
                    />

                    <InfoRow
                        icon={<CalendarClock size={18}/>}
                        label="Detection Time"
                        value={new Date(result.created_at).toLocaleString()}
                    />

                </div>

            </div>

        </Card>

    );

}