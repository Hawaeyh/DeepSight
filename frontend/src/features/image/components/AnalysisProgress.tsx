import { CheckCircle2, Circle, LoaderCircle, XCircle } from "lucide-react";

export type AnalysisStage =
    | "idle"
    | "ready"
    | "uploading"
    | "validating"
    | "detecting-face"
    | "loading-model"
    | "analysing"
    | "saving"
    | "completed"
    | "failed";

interface AnalysisProgressProps {
    stage: AnalysisStage;
    progress: number;
    message: string;
}

const LABELS: Record<AnalysisStage, string> = {
    idle: "Ready",
    ready: "Ready",
    uploading: "Uploading",
    validating: "Validating Image",
    "detecting-face": "Detecting Face",
    "loading-model": "Loading Model",
    analysing: "Analysing Image",
    saving: "Saving Result",
    completed: "Completed",
    failed: "Failed",
};

export default function AnalysisProgress({ stage, progress, message }: AnalysisProgressProps) {
    const active = !["idle", "ready", "completed", "failed"].includes(stage);
    const boundedProgress = Math.max(0, Math.min(100, progress));
    const Icon = stage === "completed" ? CheckCircle2 : stage === "failed" ? XCircle : active ? LoaderCircle : Circle;

    return <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6" aria-live="polite" role="status">
        <div className="flex items-start gap-4">
            <Icon className={`${active ? "animate-spin text-cyan-400" : stage === "completed" ? "text-green-400" : stage === "failed" ? "text-red-400" : "text-slate-400"} mt-0.5 shrink-0`} size={28} aria-hidden="true" />
            <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-4"><h2 className="font-semibold">{stage === "completed" ? "Analysis Completed" : stage === "failed" ? "Analysis Failed" : LABELS[stage]}</h2><span className="font-mono text-sm text-slate-300">{Math.round(boundedProgress)}%</span></div>
                <p className="mt-1 text-sm text-slate-400">{message}</p>
                <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-800" role="progressbar" aria-label="Image analysis progress" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(boundedProgress)} aria-valuetext={`${LABELS[stage]}, ${Math.round(boundedProgress)} percent`}>
                    <div className={`h-full rounded-full transition-[width] duration-500 ${stage === "failed" ? "bg-red-500" : stage === "completed" ? "bg-green-500" : "bg-cyan-500"}`} style={{ width: `${boundedProgress}%` }} />
                </div>
                {active && <p className="mt-3 text-xs text-slate-500">Stages are estimated while the secure server request is processing.</p>}
            </div>
        </div>
    </section>;
}
