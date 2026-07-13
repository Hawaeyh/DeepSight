import { useEffect, useState } from "react";
import { ArrowRight, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import api from "../../services/api";
import type { AdminUsageAnalytics } from "../../types/admin";
import type { ModelMetric } from "../../types/dashboard";

export default function AdminDashboardInsights({ models }: { models: ModelMetric[] }) {
    const [usage, setUsage] = useState<AdminUsageAnalytics | null>(null);

    useEffect(() => {
        api.get<AdminUsageAnalytics>("/admin/usage")
            .then(response => setUsage(response.data))
            .catch(() => undefined);
    }, []);

    return (
        <div className="grid gap-6 xl:grid-cols-2">
            <section className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                <div className="mb-5 flex items-center justify-between gap-3">
                    <div><h2 className="font-semibold">Model comparison</h2><p className="mt-1 text-sm text-slate-400">Confidence and verified performance</p></div>
                    <Link to="/admin/model-reports" className="flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300">Details <ArrowRight size={16} /></Link>
                </div>
                {models.length === 0 ? <p className="flex h-72 items-center justify-center text-sm text-slate-500">No model data yet.</p> : (
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={models} margin={{ top: 5, right: 10, left: 0, bottom: 28 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="model" stroke="#94a3b8" angle={-12} textAnchor="end" height={55} />
                                <YAxis stroke="#94a3b8" domain={[0, 100]} unit="%" />
                                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                                <Legend />
                                <Bar dataKey="averageConfidence" name="Confidence" fill="#22c55e" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="accuracy" name="Accuracy" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="precision" name="Precision" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </section>

            <section className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                <div className="mb-5 flex items-center justify-between gap-3">
                    <div><h2 className="font-semibold">User usage analytics</h2><p className="mt-1 text-sm text-slate-400">Registered-user activity over 14 days</p></div>
                    <Link to="/admin/users" className="flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300">Manage <ArrowRight size={16} /></Link>
                </div>
                <div className="mb-3 flex flex-wrap gap-5 text-sm">
                    <span className="flex items-center gap-2 text-slate-300"><Users size={17} className="text-cyan-400" />{usage?.activeUsers ?? 0} active accounts</span>
                    <span className="text-slate-400">{usage?.runsLast14Days ?? 0} runs in 14 days</span>
                </div>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={usage?.trend ?? []} margin={{ top: 5, right: 15, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" tickFormatter={value => value.slice(5)} />
                            <YAxis stroke="#94a3b8" allowDecimals={false} />
                            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                            <Legend />
                            <Line type="monotone" dataKey="runs" name="Runs" stroke="#06b6d4" strokeWidth={2} />
                            <Line type="monotone" dataKey="activeUsers" name="Active users" stroke="#22c55e" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </section>
        </div>
    );
}
