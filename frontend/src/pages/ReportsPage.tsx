import { Download, FileText, RefreshCw, Search } from "lucide-react";

import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import { useHistory } from "../features/history/hooks/useHistory";

export default function ReportsPage() {
    const { loading, error, search, setSearch, totalHistory, download, loadHistory } = useHistory();

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Investigation Reports</h1>
                <p className="mt-2 text-slate-400">Find an analysis and export its forensic PDF report.</p>
            </div>

            <div className="flex flex-wrap gap-3">
                <label className="relative min-w-64 flex-1">
                    <Search className="absolute left-3 top-3 text-slate-500" size={18} />
                    <input
                        value={search}
                        onChange={event => setSearch(event.target.value)}
                        placeholder="Search by filename"
                        className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2.5 pl-10 pr-4 outline-none focus:border-cyan-500"
                    />
                </label>
                <Button variant="secondary" onClick={loadHistory}><RefreshCw className="mr-2 inline" size={18} />Refresh</Button>
            </div>

            {error && <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-300">{error}</div>}
            {loading ? <Spinner /> : (
                <Card title="Available Reports" subtitle={`${totalHistory.length} analysis record(s)`}>
                    {totalHistory.length === 0 ? (
                        <div className="py-12 text-center text-slate-500">No matching reports.</div>
                    ) : (
                        <div className="divide-y divide-slate-800">
                            {totalHistory.map(item => (
                                <div key={item.id} className="flex flex-wrap items-center justify-between gap-4 py-4">
                                    <div className="flex min-w-0 items-center gap-3">
                                        <FileText className="shrink-0 text-cyan-400" size={24} />
                                        <div className="min-w-0">
                                            <div className="truncate font-semibold">{item.filename}</div>
                                            <div className="mt-1 text-sm text-slate-400">{item.file_type} · {item.prediction} · {new Date(item.created_at).toLocaleString()}</div>
                                        </div>
                                    </div>
                                    <Button onClick={() => download(item.id)} className="px-4 py-2"><Download className="mr-2 inline" size={18} />PDF</Button>
                                </div>
                            ))}
                        </div>
                    )}
                </Card>
            )}
        </div>
    );
}
