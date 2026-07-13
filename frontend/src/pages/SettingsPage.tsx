import { useEffect, useState } from "react";
import { CheckCircle2, Cloud, RefreshCw } from "lucide-react";

import ModelSelector from "../features/image/components/ModelSelector";
import { getDetectionModels } from "../features/image/services/image.service";
import type { DetectionModel, ModelKey } from "../types/model";
import api from "../services/api";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

interface FirebaseStatus {
    configured: boolean;
    connected: boolean;
    projectId: string | null;
    collection: string;
    error: string | null;
}

export default function SettingsPage() {
    const storedModel = localStorage.getItem("deepsight-default-model") as ModelKey | null;
    const [models, setModels] = useState<DetectionModel[]>([]);
    const [selected, setSelected] = useState<ModelKey>(storedModel ?? "efficientnet");
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [firebase, setFirebase] = useState<FirebaseStatus | null>(null);
    const [syncing, setSyncing] = useState(false);
    const [syncMessage, setSyncMessage] = useState<string | null>(null);

    useEffect(() => {
        getDetectionModels()
            .then(({ models: catalog }) => setModels(catalog))
            .catch(() => setError("Unable to load the model catalog."));
        api.get<FirebaseStatus>("/firebase/status")
            .then(response => setFirebase(response.data))
            .catch(() => setFirebase(null));
    }, []);

    function chooseModel(model: ModelKey) {
        setSelected(model);
        localStorage.setItem("deepsight-default-model", model);
        setSaved(true);
        window.setTimeout(() => setSaved(false), 2000);
    }

    async function syncFirebase() {
        try {
            setSyncing(true);
            setSyncMessage(null);
            const response = await api.post<{ total: number; synced: number }>("/firebase/sync");
            setSyncMessage(`Synced ${response.data.synced} of ${response.data.total} analyses.`);
        }
        catch (requestError: any) {
            setSyncMessage(requestError?.response?.data?.detail ?? "Firebase sync failed.");
        }
        finally {
            setSyncing(false);
        }
    }

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="mt-2 text-slate-400">
                    Configure the default network used for image analysis.
                </p>
            </div>

            {error && (
                <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-300">
                    {error}
                </div>
            )}

            <ModelSelector
                models={models}
                selected={selected}
                onChange={chooseModel}
            />

            <Card title="Firebase Storage" subtitle="Cloud Firestore analysis mirror" action={<Cloud className={firebase?.connected ? "text-green-400" : "text-slate-500"} size={28} />}>
                <div className="space-y-3 text-sm">
                    <div className="flex justify-between gap-4"><span className="text-slate-400">Status</span><span className={firebase?.connected ? "text-green-400" : "text-yellow-400"}>{firebase?.connected ? "Connected" : "Not connected"}</span></div>
                    <div className="flex justify-between gap-4"><span className="text-slate-400">Project</span><span>{firebase?.projectId ?? "Not configured"}</span></div>
                    <div className="flex justify-between gap-4"><span className="text-slate-400">Collection</span><span>{firebase?.collection ?? "analyses"}</span></div>
                    {firebase?.error && <p className="rounded-lg bg-yellow-500/10 p-3 text-yellow-300">{firebase.error}</p>}
                    <Button variant="secondary" disabled={!firebase?.connected || syncing} onClick={syncFirebase}><RefreshCw className={`mr-2 inline ${syncing ? "animate-spin" : ""}`} size={18} />{syncing ? "Syncing..." : "Sync Existing Data"}</Button>
                    {syncMessage && <p className="text-slate-300">{syncMessage}</p>}
                </div>
            </Card>

            {saved && (
                <div className="flex items-center gap-2 text-sm text-green-400" role="status">
                    <CheckCircle2 size={18} />
                    Default model saved
                </div>
            )}
        </div>
    );
}
