import { BarChart3, CheckCircle2, Database, Gauge } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import EmptyState from "../components/ui/EmptyState";
import Spinner from "../components/ui/Spinner";
import { useDashboard } from "../hooks/useDashboard";

export default function AdminModelReportsPage() {
    const { modelMetrics, loading, error } = useDashboard();

    if (loading) return <div className="flex h-[60vh] items-center justify-center"><Spinner /></div>;
    if (error) return <EmptyState title="Model reports unavailable" description={error} />;

    const totalUsage = modelMetrics.reduce((sum, item) => sum + item.usageCount, 0);
    const averageConfidence = modelMetrics.length ? modelMetrics.reduce((sum, item) => sum + item.averageConfidence, 0) / modelMetrics.length : 0;
    const verified = modelMetrics.reduce((sum, item) => sum + item.verifiedSamples, 0);

    return (
        <div className="space-y-6">
            <div>
                <p className="text-sm font-medium text-cyan-400">Administration</p>
                <h1 className="mt-1 text-3xl font-bold">Model reports</h1>
                <p className="mt-2 text-sm text-slate-400">Performance and usage calculated from completed detections and verified feedback.</p>
            </div>

            <section className="grid gap-4 sm:grid-cols-3">
                <Metric icon={Database} label="Model runs" value={totalUsage.toLocaleString()} />
                <Metric icon={Gauge} label="Average confidence" value={`${averageConfidence.toFixed(1)}%`} />
                <Metric icon={CheckCircle2} label="Verified samples" value={verified.toLocaleString()} />
            </section>

            {modelMetrics.length === 0 ? <EmptyState title="No model data" description="Run detections to populate model reports." /> : (
                <>
                    <section className="grid gap-6 xl:grid-cols-2">
                        <Chart title="Usage by model">
                            <BarChart data={modelMetrics} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="model" stroke="#94a3b8" angle={-12} textAnchor="end" height={55} />
                                <YAxis stroke="#94a3b8" unit="%" />
                                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                                <Bar dataKey="usagePercentage" name="Usage %" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </Chart>
                        <Chart title="Verified model comparison">
                            <BarChart data={modelMetrics} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="model" stroke="#94a3b8" angle={-12} textAnchor="end" height={55} />
                                <YAxis stroke="#94a3b8" domain={[0, 100]} unit="%" />
                                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                                <Legend />
                                <Bar dataKey="averageConfidence" name="Confidence" fill="#22c55e" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="accuracy" name="Verified accuracy" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="precision" name="Precision" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="recall" name="Recall" fill="#f472b6" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="f1Score" name="F1" fill="#a78bfa" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </Chart>
                    </section>

                    <section className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
                        <div className="border-b border-slate-800 px-5 py-4 font-semibold">Each model</div>
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[980px] text-left text-sm">
                                <thead className="bg-slate-800/60 text-slate-400"><tr><th className="px-5 py-3">Model</th><th className="px-5 py-3">Runs</th><th className="px-5 py-3">Usage</th><th className="px-5 py-3">Confidence</th><th className="px-5 py-3">Samples</th><th className="px-5 py-3">Accuracy</th><th className="px-5 py-3">Precision</th><th className="px-5 py-3">Recall</th><th className="px-5 py-3">F1</th></tr></thead>
                                <tbody className="divide-y divide-slate-800">{modelMetrics.map(item => <tr key={item.model}><td className="px-5 py-4 font-medium">{item.model}</td><td className="px-5 py-4">{item.usageCount}</td><td className="px-5 py-4">{item.usagePercentage.toFixed(1)}%</td><td className="px-5 py-4">{item.averageConfidence.toFixed(1)}%</td><td className="px-5 py-4">{item.verifiedSamples}</td><MetricValue value={item.accuracy} /><MetricValue value={item.precision} /><MetricValue value={item.recall} /><MetricValue value={item.f1Score} /></tr>)}</tbody>
                            </table>
                        </div>
                    </section>
                </>
            )}
        </div>
    );
}

function MetricValue({ value }: { value: number | null }) {
    return <td className="px-5 py-4">{value === null ? "Not measured" : `${value.toFixed(1)}%`}</td>;
}

function Metric({ icon: Icon, label, value }: { icon: typeof BarChart3; label: string; value: string }) {
    return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5"><div className="flex items-center gap-3 text-sm text-slate-400"><Icon size={19} />{label}</div><p className="mt-3 text-3xl font-bold">{value}</p></div>;
}

function Chart({ title, children }: { title: string; children: React.ReactElement }) {
    return <section className="rounded-lg border border-slate-800 bg-slate-900 p-5"><h2 className="mb-5 font-semibold">{title}</h2><div className="h-80"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div></section>;
}
