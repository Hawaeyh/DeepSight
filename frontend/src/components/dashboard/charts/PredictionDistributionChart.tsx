import Card from "../../ui/Card";

import {

    PieChart,

    Pie,

    Cell,

    Tooltip,

    Legend,

    ResponsiveContainer,

} from "recharts";

import type {

    PredictionDistribution,

} from "../../../types/dashboard";

interface Props {

    data: PredictionDistribution;

}

const COLORS = [

    "#22c55e",

    "#ef4444",

];

export default function PredictionDistributionChart({

    data,

}: Props) {

    const chartData = [

        {

            name: "Real",

            value: data.real,

        },

        {

            name: "Fake",

            value: data.fake,

        },

    ];

    return (

        <Card title="Prediction Distribution">

            <div className="h-80">

                <ResponsiveContainer>

                    <PieChart>

                        <Pie

                            data={chartData}

                            dataKey="value"

                            nameKey="name"

                            outerRadius={100}

                            label

                        >

                            {

                                chartData.map((_, index) => (

                                    <Cell

                                        key={index}

                                        fill={COLORS[index]}

                                    />

                                ))

                            }

                        </Pie>

                        <Tooltip />

                        <Legend />

                    </PieChart>

                </ResponsiveContainer>

            </div>

        </Card>

    );

}