import Card from "../ui/Card";

import Badge from "../ui/Badge";

import {

    Cpu,

    Brain,

    CircleCheck,

} from "lucide-react";

interface Props {

    device: string;

}

export default function AIStatusCard({

    device,

}: Props) {

    return (

        <Card title="AI Engine Status">

            <div className="space-y-5">

                <div className="flex justify-between">

                    <div className="flex gap-2 items-center">

                        <CircleCheck

                            size={18}

                            className="text-green-400"

                        />

                        <span>

                            Status

                        </span>

                    </div>

                    <Badge

                        text="Running"

                        color="green"

                    />

                </div>

                <div className="flex justify-between">

                    <div className="flex gap-2 items-center">

                        <Cpu

                            size={18}

                        />

                        <span>

                            Device

                        </span>

                    </div>

                    <span>

                        {device}

                    </span>

                </div>

                <div className="flex justify-between">

                    <div className="flex gap-2 items-center">

                        <Brain

                            size={18}

                        />

                        <span>

                            AI Engine

                        </span>

                    </div>

                    <span>

                        EfficientNet-B0

                    </span>

                </div>

            </div>

        </Card>

    );

}