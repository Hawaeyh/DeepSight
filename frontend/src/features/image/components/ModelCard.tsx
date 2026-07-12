import Card from "../../../components/ui/Card";

import type { ImageDetectionResponse } from "../types/image";

interface Props {
    result: ImageDetectionResponse | null;
}

interface ItemProps {
    label: string;
    value: string;
}

function Item({
    label,
    value,
}: ItemProps) {

    return (

        <div className="flex justify-between items-center py-3 border-b border-slate-700 last:border-b-0">

            <span className="text-slate-400 text-sm">

                {label}

            </span>

            <span className="text-white font-medium text-right">

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
                subtitle="Detection model information"
            >

                <div className="flex flex-col items-center justify-center py-12">

                    <p className="text-slate-400 font-medium">

                        No Model Information

                    </p>

                    <p className="text-slate-500 text-sm mt-2">

                        Run image detection to display model information.

                    </p>

                </div>

            </Card>

        );

    }

    return (

        <Card
            title="AI Model"
            subtitle="DeepSight Detection Model"
        >

            <div className="space-y-1">

                <Item
                    label="Model"
                    value={result.model_name}
                />

                <Item
                    label="Version"
                    value={result.model_version}
                />

                <Item
                    label="Framework"
                    value="PyTorch"
                />

                <Item
                    label="Inference Device"
                    value={result.device.toUpperCase()}
                />

                <Item
                    label="Input Resolution"
                    value="224 × 224"
                />

                <Item
                    label="Classification"
                    value="Binary"
                />

                <Item
                    label="Classes"
                    value="Real / Fake"
                />

                <Item
                    label="Architecture"
                    value="EfficientNet-B0"
                />

                <Item
                    label="Dataset"
                    value="DeepSight Binary V3"
                />

                <Item
                    label="Status"
                    value="Ready"
                />

            </div>

        </Card>

    );

}