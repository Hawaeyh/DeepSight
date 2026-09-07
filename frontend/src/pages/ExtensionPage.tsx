import { Download, MonitorCheck } from "lucide-react";

import { useAuth } from "../hooks/useAuth";

export default function ExtensionPage() {
    const { user } = useAuth();
    const pro = user?.plan === "lite";

    return (
        <div className="mx-auto max-w-5xl space-y-8">
            <div><p className="text-sm font-medium text-cyan-400">{pro ? "Lite Pro" : "Basic"}</p><h1 className="mt-1 text-3xl font-bold">DeepSight Extension</h1><p className="mt-2 text-slate-400">Detect visible images on webpages and place the result directly beside the media.</p></div>
            <section className="grid gap-8 border-y border-slate-800 py-8 md:grid-cols-[1fr_auto] md:items-center">
                <div className="flex gap-4"><MonitorCheck className="shrink-0 text-cyan-400" size={32} /><div><h2 className="text-xl font-semibold">{pro ? "Continuous Pro detection" : "Page image detection"}</h2><p className="mt-2 max-w-2xl text-slate-400">{pro ? "Scan new page images automatically as they appear, with Real or Fake labels overlaid on the source page." : "Run a page scan from the extension and receive Real or Fake labels on visible images."}</p></div></div>
                <a href="/deepsight-extension.zip" download className="flex items-center justify-center gap-2 rounded-lg bg-cyan-500 px-5 py-3 font-semibold hover:bg-cyan-400"><Download size={20} />Download Extension</a>
            </section>
            <ol className="grid gap-5 text-sm text-slate-300 md:grid-cols-3">
                <li><span className="mb-2 block font-semibold text-white">1. Install</span>Extract the ZIP and load the folder as an unpacked extension.</li>
                <li><span className="mb-2 block font-semibold text-white">2. Sign in</span>Open the extension and use your DeepSight account.</li>
                <li><span className="mb-2 block font-semibold text-white">3. Detect</span>Scan the current page and review labels on its images.</li>
            </ol>
        </div>
    );
}
