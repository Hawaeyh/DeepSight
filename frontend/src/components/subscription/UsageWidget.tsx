import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../services/api";
import type { UsageStatus } from "../../types/auth";

export default function UsageWidget() {
    const [status, setStatus] = useState<UsageStatus | null>(null);

    useEffect(() => {
        const load = () => api.get<UsageStatus>("/subscriptions/status").then(response => setStatus(response.data)).catch(() => undefined);
        load();
        const timer = window.setInterval(load, 10000);
        return () => window.clearInterval(timer);
    }, []);

    if (!status) return null;
    const limit = status.plan.limit;
    const percentage = limit ? Math.min((status.used / limit) * 100, 100) : 0;

    return (
        <Link to="/plans" className="mx-4 mb-4 block rounded-lg border border-slate-700 bg-slate-800/60 p-3 hover:border-cyan-500">
            <div className="flex justify-between text-xs"><span className="font-semibold text-cyan-300">{status.plan.name}</span><span className="text-slate-400">{status.remaining === null ? "Unlimited" : `${status.remaining} left`}</span></div>
            {limit && <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-700"><div className="h-full bg-cyan-500" style={{ width: `${percentage}%` }} /></div>}
            <p className="mt-2 text-[11px] text-slate-500">View plans and limits</p>
        </Link>
    );
}
