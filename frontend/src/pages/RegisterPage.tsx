import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Button from "../components/ui/Button";
import GoogleSignInButton from "../components/auth/GoogleSignInButton";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [form, setForm] = useState({ fullName: "", email: "", password: "" });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        try { setLoading(true); setError(null); await register(form.fullName, form.email, form.password); navigate("/dashboard"); }
        catch (requestError: any) { setError(requestError?.response?.data?.detail ?? "Unable to create account."); }
        finally { setLoading(false); }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-slate-950 p-5 text-white">
            <div className="w-full max-w-md">
                <div className="mb-6 text-center"><img src="/deepsight-logo.png" alt="DeepSight System" className="mx-auto h-20 w-20 rounded-lg object-cover" /><h1 className="mt-3 text-2xl font-bold">Create your Starter account</h1><p className="mt-2 text-sm text-slate-400">10 detections every 12 hours, reports, and history.</p></div>
                <form onSubmit={submit} className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <label className="block"><span className="mb-2 block text-sm">Full name</span><input required value={form.fullName} onChange={event => setForm({ ...form, fullName: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3" /></label>
                    <label className="block"><span className="mb-2 block text-sm">Email</span><input required type="email" value={form.email} onChange={event => setForm({ ...form, email: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3" /></label>
                    <label className="block"><span className="mb-2 block text-sm">Password</span><input required minLength={8} type="password" value={form.password} onChange={event => setForm({ ...form, password: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3" /><span className="mt-1 block text-xs text-slate-500">At least 8 characters.</span></label>
                    {error && <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}
                    <Button type="submit" disabled={loading} className="w-full">{loading ? "Creating account..." : "Create Account"}</Button>
                    <GoogleSignInButton />
                    <p className="text-center text-sm text-slate-400">Already registered? <Link to="/login" className="text-cyan-400">Sign in</Link></p>
                </form>
            </div>
        </main>
    );
}
