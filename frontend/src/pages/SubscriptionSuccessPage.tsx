import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import type { UsageStatus } from "../types/auth";

export default function SubscriptionSuccessPage() {
    const [status, setStatus] = useState<UsageStatus | null>(null);
    const [finished, setFinished] = useState(false);
    useEffect(() => {
        let attempts = 0; let active = true;
        const poll = async () => {
            try { const response = await api.get<UsageStatus>("/subscriptions/current"); if (!active) return; setStatus(response.data); if (["active", "trialing"].includes(response.data.subscriptionStatus ?? "")) { setFinished(true); return; } }
            catch { /* bounded retry below */ }
            attempts += 1; if (attempts < 10 && active) window.setTimeout(poll, 2000); else if (active) setFinished(true);
        };
        void poll(); return () => { active = false; };
    }, []);
    const activePlan = ["active", "trialing"].includes(status?.subscriptionStatus ?? "");
    return <main className="mx-auto max-w-xl p-8 text-center"><h1 className="text-3xl font-bold">Subscription confirmation</h1><p className="mt-4 text-slate-300">{activePlan ? `Your ${status?.plan.name} plan is active.` : finished ? "Your payment is being confirmed. Refresh shortly." : "Payment received. Confirming your subscription..."}</p><Link className="mt-6 inline-block text-cyan-400" to="/plans">Return to plans</Link></main>;
}
