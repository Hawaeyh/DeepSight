import { useEffect, useState } from "react";
import { Check, Crown } from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import Button from "../components/ui/Button";
import { useAuth } from "../context/AuthContext";
import type { Plan, UsageStatus } from "../types/auth";

export default function PlansPage() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [plans, setPlans] = useState<Plan[]>([]);
    const [usage, setUsage] = useState<UsageStatus | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    useEffect(() => {
        Promise.all([
            api.get<Plan[]>("/subscriptions/plans"),
            api.get<UsageStatus>("/subscriptions/status"),
        ]).then(([planResponse, usageResponse]) => {
            setPlans(planResponse.data);
            setUsage(usageResponse.data);
        });
    }, []);

    function choose(plan: Plan) {
        if (!user && plan.key === "starter") { navigate("/register"); return; }
        if (!user) { navigate("/register"); return; }
        if (plan.key === usage?.plan.key) return;
        setMessage("Online payment is not configured yet. Add a payment provider before activating paid plans.");
    }

    return (
        <div className="space-y-8">
            <div><h1 className="text-3xl font-bold">Subscription Plans</h1><p className="mt-2 text-slate-400">Choose the detection allowance and features that fit your work.</p></div>
            {usage && <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 p-4 text-cyan-100">Current access: <strong>{usage.plan.name}</strong> · {usage.remaining === null ? "Unlimited detections" : `${usage.remaining} detections remaining`}</div>}
            {message && <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-yellow-200">{message}</div>}
            <div className="grid gap-6 xl:grid-cols-3">
                {plans.map(plan => {
                    const current = plan.key === usage?.plan.key;
                    return (
                        <section key={plan.key} className={`border p-6 ${current ? "border-cyan-400 bg-cyan-500/5" : "border-slate-700 bg-slate-900"} rounded-lg`}>
                            <div className="flex items-center justify-between"><h2 className="text-2xl font-bold">{plan.name}</h2>{plan.key === "lite" && <Crown className="text-yellow-400" size={25} />}</div>
                            <div className="mt-4 text-2xl font-semibold text-cyan-300">{plan.price}</div>
                            <p className="mt-2 text-sm text-slate-400">{plan.limit === null ? "Unlimited detections" : `${plan.limit} detections every ${plan.windowHours} hours`}</p>
                            <ul className="my-6 space-y-3">{plan.features.map(feature => <li key={feature} className="flex gap-2 text-sm text-slate-300"><Check className="shrink-0 text-green-400" size={18} />{feature}</li>)}</ul>
                            <Button className="w-full" variant={current ? "secondary" : "primary"} onClick={() => choose(plan)} disabled={current}>{current ? "Current Plan" : plan.key === "starter" ? "Start Free" : "Subscribe"}</Button>
                        </section>
                    );
                })}
            </div>
            <p className="text-sm text-slate-500">Guest access includes 2 detections per day without registration. Paid subscriptions require payment-provider configuration before activation.</p>
        </div>
    );
}
