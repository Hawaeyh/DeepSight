import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Button from "../components/ui/Button";
import GoogleSignInButton from "../components/auth/GoogleSignInButton";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        try { setLoading(true); setError(null); await login(email, password); navigate("/dashboard"); }
        catch (requestError: any) { setError(requestError?.response?.data?.detail ?? "Unable to sign in."); }
        finally { setLoading(false); }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-slate-950 p-5 text-white">
            <div className="w-full max-w-md">
                <div className="mb-8 text-center"><img src="/deepsight-logo.png" alt="DeepSight System" className="mx-auto h-24 w-24 rounded-lg object-cover" /><h1 className="mt-4 text-3xl font-bold">DeepSight System</h1><p className="mt-2 text-sm text-slate-400">Machine Learning-Driven Deepfake Image Detection System</p></div>
                <form onSubmit={submit} className="space-y-5 rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div><h2 className="text-xl font-semibold">Sign in</h2><p className="mt-1 text-sm text-slate-400">Continue to your detection workspace.</p></div>
                    <label className="block"><span className="mb-2 block text-sm">Email</span><input required type="email" value={email} onChange={event => setEmail(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-cyan-500" /></label>
                    <label className="block"><span className="mb-2 block text-sm">Password</span><input required type="password" value={password} onChange={event => setPassword(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-cyan-500" /></label>
                    {error && <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}
                    <Button type="submit" disabled={loading} className="w-full">{loading ? "Signing in..." : "Sign In"}</Button>
                    <div className="flex items-center gap-3 text-xs text-slate-500"><span className="h-px flex-1 bg-slate-700" />OR<span className="h-px flex-1 bg-slate-700" /></div>
                    <GoogleSignInButton />
                    <p className="text-center text-sm text-slate-400">No account? <Link to="/register" className="text-cyan-400 hover:underline">Create one</Link></p>
                    <p className="text-center text-xs text-slate-500"><Link to="/">Continue as guest (2 detections daily)</Link></p>
                </form>
            </div>
        </main>
    );
}
