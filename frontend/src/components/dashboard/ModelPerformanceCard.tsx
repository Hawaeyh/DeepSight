import { Activity, BadgeCheck, Crosshair, Gauge } from "lucide-react";

import Card from "../ui/Card";
import ProgressBar from "../ui/ProgressBar";
import type { ModelMetric } from "../../types/dashboard";

interface Props {
    data: ModelMetric[];
}

export default function ModelPerformanceCard({ data }: Props) {
    return (
        <Card title="Model Analytics" subtitle="Usage and human-verified performance">
            {data.length === 0 ? (
                <div className="py-12 text-center text-slate-500">No model usage recorded yet.</div>
            ) : (
                <div className="space-y-6">
                    {data.map(item => (
                        <div key={item.model} className="border-b border-slate-800 pb-6 last:border-0 last:pb-0">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div>
                                    <h3 className="font-semibold">{item.model}</h3>
                                    <p className="mt-1 text-sm text-slate-400">{item.usageCount} analyses</p>
                                </div>
                                <div className="flex flex-wrap gap-4 text-sm">
                                    <span className="flex items-center gap-2 text-cyan-300">
                                        <Activity size={16} /> {item.usagePercentage.toFixed(1)}% usage
                                    </span>
                                    <span className="flex items-center gap-2 text-blue-300">
                                        <Gauge size={16} /> {item.averageConfidence.toFixed(1)}% confidence
                                    </span>
                                    <span className="flex items-center gap-2 text-green-300">
                                        <BadgeCheck size={16} />
                                        {item.accuracy === null
                                            ? "Accuracy not measured"
                                            : `${item.accuracy.toFixed(1)}% accuracy`}
                                    </span>
                                    <span className="flex items-center gap-2 text-sky-300">
                                        <Crosshair size={16} />
                                        {item.precision === null
                                            ? "Precision not measured"
                                            : `${item.precision.toFixed(1)}% precision`}
                                    </span>
                                </div>
                            </div>
                            <div className="mt-4">
                                <ProgressBar value={item.usagePercentage} />
                            </div>
                            <p className="mt-2 text-xs text-slate-500">
                                {item.verifiedSamples} human-verified sample(s)
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}
