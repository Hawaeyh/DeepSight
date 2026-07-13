import Card from "../../../components/ui/Card";

import {

    Activity,
    Image,
    ShieldCheck,
    ShieldAlert,

} from "lucide-react";

import type {

    HistoryItem,

} from "../types/history";

interface Props {

    history: HistoryItem[];

}

export default function HistoryStatistics({

    history,

}: Props) {

    const total = history.length;

    const real = history.filter(

        item => item.prediction === "Real",

    ).length;

    const fake = history.filter(

        item => item.prediction === "Fake",

    ).length;

    const today = history.filter(item => {

        const created = new Date(item.created_at);

        const now = new Date();

        return (

            created.getFullYear() === now.getFullYear() &&

            created.getMonth() === now.getMonth() &&

            created.getDate() === now.getDate()

        );

    }).length;

    return (

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

            <StatCard

                title="Total Detection"

                value={total}

                icon={<Image size={34}/>}

            />

            <StatCard

                title="Real Images"

                value={real}

                icon={<ShieldCheck size={34}/>}

            />

            <StatCard

                title="Fake Images"

                value={fake}

                icon={<ShieldAlert size={34}/>}

            />

            <StatCard

                title="Today"

                value={today}

                icon={<Activity size={34}/>}

            />

        </div>

    );

}

interface StatProps {

    title: string;

    value: number;

    icon: React.ReactNode;

}

function StatCard({

    title,

    value,

    icon,

}: StatProps) {

    return (

        <Card

            title={title}

        >

            <div className="flex justify-between items-center">

                <h2 className="text-3xl font-bold">

                    {value}

                </h2>

                <div className="text-cyan-400">

                    {icon}

                </div>

            </div>

        </Card>

    );

}