import { useEffect, useState } from "react";
import { ArrowRight, Clock3, FileSearch, Image, LogIn, Video } from "lucide-react";
import { Link } from "react-router-dom";

import Spinner from "../components/ui/Spinner";
import { useAuth } from "../hooks/useAuth";
import { useDashboard } from "../hooks/useDashboard";
import api from "../services/api";
import type { UsageStatus } from "../types/auth";

export default function UserDashboardPage() {
    const { user } = useAuth();
    const { overview, recent, loading } = useDashboard();
    const [usage, setUsage] = useState<UsageStatus | null>(null);

    useEffect(() => {
        api.get<UsageStatus>("/subscriptions/status").then(response => setUsage(response.data)).catch(() => undefined);
    }, []);

    if (loading) return <div className="flex h-[60vh] items-center justify-center"><Spinner /></div>;

    const firstName = user?.full_name?.split(" ")[0];
    const usageLabel = usage?.remaining === null ? "Unlimited" : `${usage?.remaining ?? 0} remaining`;

    return (
        <div className="mx-auto max-w-6xl space-y-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-cyan-400">{user ? usage?.plan.name ?? user.plan : "Guest access"}</p>
                    <h1 className="mt-1 text-2xl font-bold md:text-3xl">{firstName ? `Welcome, ${firstName}` : "Deepfake detection"}</h1>
                </div>
                {!user && <Link to="/login" className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 font-semibold text-white hover:bg-cyan-400"><LogIn size={18} />Sign In</Link>}
            </div>

            <section className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <div className="flex items-center gap-3 text-slate-400"><FileSearch size={19} /><span className="text-sm">Total analyses</span></div>
                    <p className="mt-3 text-3xl font-bold">{overview?.totalDetection ?? 0}</p>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <div className="flex items-center gap-3 text-slate-400"><Clock3 size={19} /><span className="text-sm">Today</span></div>
                    <p className="mt-3 text-3xl font-bold">{overview?.todayDetection ?? 0}</p>
                </div>
                <Link to="/plans" className="rounded-lg border border-slate-800 bg-slate-900 p-5 hover:border-cyan-500">
                    <div className="flex items-center justify-between text-slate-400"><span className="text-sm">Detection allowance</span><ArrowRight size={18} /></div>
                    <p className="mt-3 text-2xl font-bold text-cyan-400">{usageLabel}</p>
                </Link>
            </section>

            <section>
                <h2 className="mb-3 text-lg font-semibold">Start a detection</h2>
                <div className="grid gap-4 sm:grid-cols-2">
                    <Link to="/image" className="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-900 p-5 hover:border-cyan-500">
                        <span className="rounded-lg bg-cyan-500/15 p-3 text-cyan-400"><Image size={26} /></span>
                        <span><span className="block font-semibold">Check an image</span><span className="mt-1 block text-sm text-slate-400">Upload an image for analysis</span></span>
                        <ArrowRight className="ml-auto text-slate-500" size={20} />
                    </Link>
                    <Link to="/video" className="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-900 p-5 hover:border-cyan-500">
                        <span className="rounded-lg bg-emerald-500/15 p-3 text-emerald-400"><Video size={26} /></span>
                        <span><span className="block font-semibold">Check a video</span><span className="mt-1 block text-sm text-slate-400">Analyze sampled video frames</span></span>
                        <ArrowRight className="ml-auto text-slate-500" size={20} />
                    </Link>
                </div>
            </section>

            <section className="rounded-lg border border-slate-800 bg-slate-900">
                <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
                    <h2 className="font-semibold">Recent analyses</h2>
                    <Link to="/history" className="text-sm text-cyan-400 hover:text-cyan-300">View history</Link>
                </div>
                <div className="divide-y divide-slate-800">
                    {recent.slice(0, 5).map(item => (
                        <div key={item.id} className="flex items-center gap-3 px-5 py-4">
                            <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${item.prediction === "Fake" ? "bg-red-400" : "bg-emerald-400"}`} />
                            <span className="min-w-0 flex-1"><span className="block truncate font-medium">{item.filename}</span><span className="text-xs text-slate-500">{item.model} · {new Date(item.createdAt).toLocaleString()}</span></span>
                            <span className={item.prediction === "Fake" ? "text-red-400" : "text-emerald-400"}>{item.prediction}</span>
                        </div>
                    ))}
                    {recent.length === 0 && <p className="p-8 text-center text-sm text-slate-500">No analyses yet.</p>}
                </div>
            </section>
        </div>
    );
}
