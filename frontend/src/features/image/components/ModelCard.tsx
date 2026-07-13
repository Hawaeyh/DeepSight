import Card from "../../../components/ui/Card";

import {
    BrainCircuit,
    Cpu,
    Database,
    Layers3,
    Monitor,
    ShieldCheck,
    Gauge,
    Box,
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

export default function ModelCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card
                title="AI Model"
                subtitle="DeepSight Detection Model"
            >

                <div className="py-16 text-center text-slate-500">

                    Analyze an image to view model information.

                </div>

            </Card>

        );

    }

    return (

        <Card
            title="AI Model"
            subtitle="DeepSight Detection Model"
        >

            <div className="space-y-6">

                <div className="text-center">

                    <BrainCircuit
                        size={60}
                        className="mx-auto text-blue-500"
                    />

                    <h2 className="text-2xl font-bold mt-4">

                        {result.model_name}

                    </h2>

                    <p className="text-slate-400 mt-2">

                        Version {result.model_version}

                    </p>

                </div>

                <div className="border-t border-slate-700 pt-4">

                    <InfoRow
                        icon={<BrainCircuit size={18}/>}
                        label="Model"
                        value={result.model_name}
                    />

                    <InfoRow
                        icon={<Box size={18}/>}
                        label="Version"
                        value={result.model_version}
                    />

                    <InfoRow
                        icon={<Cpu size={18}/>}
                        label="Framework"
                        value="PyTorch"
                    />

                    <InfoRow
                        icon={<Monitor size={18}/>}
                        label="Inference Device"
                        value={result.device.toUpperCase()}
                    />

                    <InfoRow
                        icon={<Layers3 size={18}/>}
                        label="Input Resolution"
                        value="224 × 224"
                    />

                    <InfoRow
                        icon={<ShieldCheck size={18}/>}
                        label="Classification"
                        value="Binary"
                    />

                    <InfoRow
                        icon={<Database size={18}/>}
                        label="Dataset"
                        value={`${result.model_name} ${result.model_version}`}
                    />

                    <InfoRow
                        icon={<Gauge size={18}/>}
                        label="Inference Speed"
                        value={`${result.processing_time.toFixed(2)} sec`}
                    />

                </div>

                <div className="border-t border-slate-700 pt-5">

                    <div className="flex items-center justify-between">

                        <span className="text-slate-400">

                            Model Status

                        </span>

                        <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-semibold">

                            READY

                        </span>

                    </div>

                </div>

            </div>

        </Card>

    );

}
