import { Link } from "react-router-dom";
export default function SubscriptionCancelPage() { return <main className="mx-auto max-w-xl p-8 text-center"><h1 className="text-3xl font-bold">Checkout cancelled</h1><p className="mt-4 text-slate-300">Checkout was cancelled. No plan changes were made.</p><Link className="mt-6 inline-block text-cyan-400" to="/plans">Return to plans</Link></main>; }
