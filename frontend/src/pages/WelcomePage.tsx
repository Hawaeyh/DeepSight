import { ArrowRight, Image, LogIn, ShieldCheck, UserPlus } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function WelcomePage() {
    const { user } = useAuth();

    return (
        <main className="min-h-screen bg-slate-950 text-white">
            <header className="absolute inset-x-0 top-0 z-20 flex h-20 items-center justify-between px-5 md:px-10">
                <Link to="/" className="flex items-center gap-3"><img src="/deepsight-logo.png" alt="DeepSight System" className="h-11 w-11 rounded-lg object-cover" /><span className="font-bold">DeepSight System</span></Link>
                <nav className="flex items-center gap-2">
                    {user ? <Link to="/dashboard" className="rounded-lg bg-cyan-500 px-4 py-2 font-semibold hover:bg-cyan-400">Dashboard</Link> : <><Link to="/login" className="flex items-center gap-2 rounded-lg px-3 py-2 text-slate-200 hover:bg-slate-900"><LogIn size={18} />Login</Link><Link to="/register" className="hidden items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 font-semibold hover:bg-cyan-400 sm:flex"><UserPlus size={18} />Sign Up</Link></>}
                </nav>
            </header>

            <section className="relative flex min-h-[78vh] items-center overflow-hidden border-b border-slate-800 px-5 pt-20 md:px-10">
                <img src="/deepsight-logo.png" alt="" className="pointer-events-none absolute right-[-8%] top-[12%] h-[76%] max-w-[70vw] object-contain opacity-20" />
                <div className="relative z-10 max-w-3xl">
                    <p className="font-semibold text-cyan-400">Machine Learning-Driven Deepfake Image Detection System</p>
                    <h1 className="mt-4 text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">DeepSight System</h1>
                    <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">Inspect suspicious media, understand manipulation signals, and verify whether visual content is real or fake.</p>
                    <div className="mt-8 flex flex-wrap gap-3">
                        <Link to="/image" className="flex items-center gap-2 rounded-lg bg-cyan-500 px-5 py-3 font-semibold hover:bg-cyan-400"><Image size={20} />Test an Image</Link>
                        <Link to={user ? "/dashboard" : "/register"} className="flex items-center gap-2 rounded-lg border border-slate-600 px-5 py-3 font-semibold hover:border-cyan-400 hover:bg-slate-900">Explore DeepSight <ArrowRight size={20} /></Link>
                    </div>
                </div>
            </section>

            <section className="mx-auto grid max-w-6xl gap-8 px-5 py-12 md:grid-cols-3 md:px-10">
                <Feature title="Public image trial" text="Test image authenticity before creating an account." />
                <Feature title="Personal workspace" text="Sign in for video analysis, history, reports, and feedback." />
                <Feature title="Detection everywhere" text="Subscribers can use the extension and Lite live detection." />
            </section>
        </main>
    );
}

function Feature({ title, text }: { title: string; text: string }) {
    return <div className="border-l-2 border-cyan-500 pl-5"><ShieldCheck className="text-cyan-400" size={24} /><h2 className="mt-4 text-lg font-semibold">{title}</h2><p className="mt-2 leading-6 text-slate-400">{text}</p></div>;
}
