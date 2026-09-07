import { useEffect, useState } from "react";

import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";
import api from "../services/api";

interface AdminAnalysis {
    id: number; createdAt: string; mediaType: string; source: string; prediction: string;
    confidence: number; status: string; ownershipType: "owned" | "guest" | "legacy";
    owner: string | null; modelName: string;
}
interface Page { items: AdminAnalysis[]; page: number; pageSize: number; total: number }

export default function AdminAnalysesPage() {
    const [data, setData] = useState<Page | null>(null);
    const [ownership, setOwnership] = useState("all");
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setLoading(true);
        api.get<Page>("/admin/analyses", { params: { ownership, page, page_size: 25 } })
            .then(response => { setData(response.data); setError(null); })
            .catch(() => setError("Unable to load administrator analysis history."))
            .finally(() => setLoading(false));
    }, [ownership, page]);

    return <div className="space-y-6">
        <div><p className="text-sm font-medium text-cyan-400">Administration</p><h1 className="mt-1 text-3xl font-bold">All analyses</h1><p className="mt-2 text-sm text-slate-400">Owned, guest, and legacy records. Media remains protected.</p></div>
        <label className="block max-w-xs text-sm">Ownership<select value={ownership} onChange={event => { setOwnership(event.target.value); setPage(1); }} className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"><option value="all">All records</option><option value="owned">Registered users</option><option value="guest">Guests</option><option value="legacy">Legacy unowned</option></select></label>
        {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>}
        {loading ? <div className="flex h-60 items-center justify-center"><Spinner /></div> : <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900"><table className="w-full min-w-[900px] text-left text-sm"><thead className="bg-slate-800/60 text-slate-400"><tr><th className="px-4 py-3">ID</th><th className="px-4 py-3">Ownership</th><th className="px-4 py-3">Owner</th><th className="px-4 py-3">Media / source</th><th className="px-4 py-3">Result</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Date</th></tr></thead><tbody className="divide-y divide-slate-800">{data?.items.map(item => <tr key={item.id}><td className="px-4 py-3">{item.id}</td><td className="px-4 py-3"><span className="rounded-full bg-slate-700 px-2 py-1 text-xs capitalize">{item.ownershipType}</span></td><td className="px-4 py-3">{item.owner ?? (item.ownershipType === "guest" ? "Verified guest" : "No historical owner")}</td><td className="px-4 py-3">{item.mediaType}<span className="block text-xs text-slate-500">{item.source}</span></td><td className="px-4 py-3">{item.prediction}<span className="block text-xs text-slate-500">{item.confidence.toFixed(1)}%</span></td><td className="px-4 py-3">{item.status}</td><td className="px-4 py-3 text-slate-400">{new Date(item.createdAt).toLocaleString()}</td></tr>)}</tbody></table>{data?.items.length === 0 && <p className="p-8 text-center text-slate-500">No matching analyses.</p>}</div>}
        <div className="flex items-center justify-between"><span className="text-sm text-slate-400">{data?.total ?? 0} records</span><div className="flex gap-2"><Button variant="secondary" disabled={page <= 1} onClick={() => setPage(value => value - 1)}>Previous</Button><Button variant="secondary" disabled={!data || page * data.pageSize >= data.total} onClick={() => setPage(value => value + 1)}>Next</Button></div></div>
    </div>;
}
