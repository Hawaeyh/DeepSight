import Card from "../ui/Card";

import type {

    RecentDetection,

} from "../../types/dashboard";

interface Props {

    data: RecentDetection[];

}

export default function RecentDetectionTable({

    data,

}: Props) {

    return (

        <Card title="Recent Detection">

            <div className="overflow-x-auto">

                <table className="w-full">

                    <thead>

                        <tr className="border-b border-slate-800 text-slate-400 text-sm">

                            <th className="text-left py-3">

                                Filename

                            </th>

                            <th className="text-left py-3">

                                Prediction

                            </th>

                            <th className="text-left py-3">

                                Confidence

                            </th>

                            <th className="text-left py-3">

                                Risk

                            </th>

                            <th className="text-left py-3">

                                Date

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {

                            data.length === 0 ? (

                                <tr>

                                    <td

                                        colSpan={5}

                                        className="py-8 text-center text-slate-500"

                                    >

                                        No detection history found.

                                    </td>

                                </tr>

                            ) : (

                                data.map((item) => (

                                    <tr

                                        key={item.id}

                                        className="border-b border-slate-800 hover:bg-slate-800/40 transition"

                                    >

                                        <td className="py-4">

                                            {item.filename}

                                        </td>

                                        <td className="py-4">

                                            <span

                                                className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                    item.prediction === "Fake"
                                                        ? "bg-red-500/20 text-red-400"
                                                        : "bg-green-500/20 text-green-400"
                                                }`}

                                            >

                                                {item.prediction}

                                            </span>

                                        </td>

                                        <td className="py-4">

                                            {item.confidence.toFixed(2)}%

                                        </td>

                                        <td className="py-4">

                                            {item.riskLevel}

                                        </td>

                                        <td className="py-4 text-slate-400">

                                            {

                                                new Date(

                                                    item.createdAt

                                                ).toLocaleString()

                                            }

                                        </td>

                                    </tr>

                                ))

                            )

                        }

                    </tbody>

                </table>

            </div>

        </Card>

    );

}