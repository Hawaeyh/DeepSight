import { useEffect, useState } from "react";
import { Check, Crown } from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import Button from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";
import type { Plan, UsageStatus } from "../types/auth";

export default function PlansPage() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [plans, setPlans] = useState<Plan[]>([]);
    const [usage, setUsage] = useState<UsageStatus | null>(null);
    const [message, setMessage] = useState<string | null>(null);
    const [interval, setInterval] = useState<"monthly" | "annual">("monthly");
    const [busyPlan, setBusyPlan] = useState<string | null>(null);
    const [payments, setPayments] = useState<"ok" | "not_configured" | "failed">("not_configured");

    useEffect(() => {
        Promise.all([
            api.get<Plan[]>("/subscriptions/plans"),
            api.get<UsageStatus>("/subscriptions/status"),
            api.get<{status:"ok"|"not_configured"|"failed"}>("/health/payments"),
        ]).then(([planResponse, usageResponse, paymentResponse]) => {
            setPlans(planResponse.data);
            setUsage(usageResponse.data);
            setPayments(paymentResponse.data.status);
        });
    }, []);

    async function choose(plan: Plan) {
        if (!user && plan.key === "starter") { navigate("/register"); return; }
        if (!user) { navigate("/register"); return; }
        if (plan.key === usage?.plan.key) return;
        try {
            setBusyPlan(plan.key);
            setMessage(null);
            const response = await api.post<{checkoutUrl:string}>("/subscriptions/checkout", { plan_code: plan.key, billing_period: interval });
            window.location.assign(response.data.checkoutUrl);
        } catch (error: any) {
            setMessage(error?.response?.data?.detail?.message ?? error?.response?.data?.detail ?? "Test-mode checkout is not configured.");
        } finally { setBusyPlan(null); }
    }

    async function manage() {
        try { setMessage(null); const response = await api.post<{portalUrl:string}>("/subscriptions/portal"); window.location.assign(response.data.portalUrl); }
        catch (error: any) { setMessage(error?.response?.data?.detail?.message ?? error?.response?.data?.detail ?? "Billing management is unavailable."); }
    }

    return (
        <div className="space-y-8">
            <div><h1 className="text-3xl font-bold">Subscription Plans</h1><p className="mt-2 text-slate-400">Choose the detection allowance and features that fit your work.</p></div>
            {usage && <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 p-4 text-cyan-100">Current access: <strong>{user?.role === "admin" ? "Admin • Lite" : usage.plan.name}</strong> · {user?.role === "admin" ? "Unlimited detections and all premium features" : usage.remaining === null ? "Unlimited detections" : `${usage.remaining} detections remaining`}</div>}
            {message && <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-yellow-200">{message}</div>}
            {user && usage?.hasBillingCustomer && <Button variant="secondary" onClick={manage}>Manage Subscription</Button>}
            {payments !== "ok" && <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-yellow-200">Purchasing is currently unavailable because Stripe test mode is not configured.</div>}
            <div className="flex gap-2"><Button variant={interval === "monthly" ? "primary" : "secondary"} onClick={() => setInterval("monthly")}>Monthly</Button><Button variant={interval === "annual" ? "primary" : "secondary"} onClick={() => setInterval("annual")}>Annual</Button></div>
            <div className="grid gap-6 xl:grid-cols-3">
                {plans.map(plan => {
                    const current = plan.key === usage?.plan.key;
                    return (
                        <section key={plan.key} className={`border p-6 ${current ? "border-cyan-400 bg-cyan-500/5" : "border-slate-700 bg-slate-900"} rounded-lg`}>
                            <div className="flex items-center justify-between"><h2 className="text-2xl font-bold">{plan.name}</h2>{plan.key === "lite" && <Crown className="text-yellow-400" size={25} />}</div>
                            <div className="mt-4 text-2xl font-semibold text-cyan-300">{interval === "annual" && plan.annualPrice ? `RM ${plan.annualPrice}/year` : plan.price}</div>
                            <p className="mt-2 text-sm text-slate-400">{plan.limit === null ? "Unlimited detections" : `${plan.limit} detections every ${plan.windowHours} hours`}</p>
                            <ul className="my-6 space-y-3">{plan.features.map(feature => <li key={feature} className="flex gap-2 text-sm text-slate-300"><Check className="shrink-0 text-green-400" size={18} />{feature}</li>)}</ul>
                            <Button className="w-full" variant={current ? "secondary" : "primary"} onClick={() => choose(plan)} disabled={current || busyPlan === plan.key || (plan.key !== "starter" && (payments !== "ok" || !plan.billingAvailable?.[interval]))}>{current ? "Current Plan" : !user ? "Login to Purchase" : busyPlan === plan.key ? "Opening Checkout..." : plan.key === "starter" ? "Start Free" : payments !== "ok" || !plan.billingAvailable?.[interval] ? "Unavailable" : interval === "monthly" ? "Choose Monthly" : "Choose Annual"}</Button>
                        </section>
                    );
                })}
            </div>
            <p className="text-sm text-slate-500">Guest access includes 2 detections per day without registration. Paid subscriptions require payment-provider configuration before activation.</p>
        </div>
    );
}
