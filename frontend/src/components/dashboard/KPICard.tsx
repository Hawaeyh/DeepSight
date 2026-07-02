import type { LucideIcon } from "lucide-react";

import Card from "../ui/Card";

interface Props {

    title: string;

    value: string | number;

    subtitle?: string;

    color?: string;

    icon: LucideIcon;

}

export default function KPICard({

    title,

    value,

    subtitle,

    color = "text-cyan-400",

    icon: Icon,

}: Props) {

    return (

        <Card>

            <div className="flex justify-between items-start">

                <div>

                    <p className="text-slate-400 text-sm">

                        {title}

                    </p>

                    <h2 className="mt-3 text-4xl font-bold">

                        {value}

                    </h2>

                    {

                        subtitle && (

                            <p className="mt-2 text-sm text-slate-500">

                                {subtitle}

                            </p>

                        )

                    }

                </div>

                <div className={`p-3 rounded-xl bg-slate-800 ${color}`}>

                    <Icon size={28} />

                </div>

            </div>

        </Card>

    );

}