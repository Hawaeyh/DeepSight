import Card from "../../ui/Card";

import {

    ResponsiveContainer,

    LineChart,

    Line,

    XAxis,

    YAxis,

    CartesianGrid,

    Tooltip,

} from "recharts";

import type {

    DetectionTrend,

} from "../../../types/dashboard";

interface Props {

    data: DetectionTrend[];

}

export default function DetectionTrendChart({

    data,

}: Props) {

    return (

        <Card title="Detection Trend">

            <div className="h-80">

                <ResponsiveContainer width="100%" height="100%">

                    <LineChart

                        data={data}

                    >

                        <CartesianGrid

                            stroke="#1e293b"

                            strokeDasharray="4 4"

                        />

                        <XAxis

                            dataKey="date"

                            stroke="#94a3b8"

                        />

                        <YAxis

                            stroke="#94a3b8"

                        />

                        <Tooltip

                            contentStyle={{

                                background: "#0f172a",

                                border: "1px solid #334155",

                                borderRadius: 12,

                            }}

                        />

                        <Line

                            type="monotone"

                            dataKey="count"

                            stroke="#06b6d4"

                            strokeWidth={3}

                            dot={false}

                            activeDot={{

                                r: 6,

                            }}

                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>

        </Card>

    );

}