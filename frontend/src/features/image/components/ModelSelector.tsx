import { BrainCircuit, CheckCircle2, LockKeyhole } from "lucide-react";

import Card from "../../../components/ui/Card";
import type { DetectionModel, ModelKey } from "../../../types/model";

interface Props {
    models: DetectionModel[];
    selected: ModelKey;
    disabled?: boolean;
    onChange(model: ModelKey): void;
}

export default function ModelSelector({
    models,
    selected,
    disabled = false,
    onChange,
}: Props) {
    return (
        <Card title="Detection Model" subtitle="Choose the network used for this analysis">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {models.map(model => {
                    const active = model.key === selected;
                    const unavailable = !model.available;

                    return (
                        <button
                            key={model.key}
                            type="button"
                            disabled={disabled || unavailable}
                            title={unavailable ? "A trained checkpoint is required" : model.description}
                            onClick={() => onChange(model.key)}
                            className={`min-h-28 rounded-lg border p-4 text-left transition ${
                                active
                                    ? "border-cyan-400 bg-cyan-500/10"
                                    : "border-slate-700 bg-slate-800/60 hover:border-slate-500"
                            } disabled:cursor-not-allowed disabled:opacity-50`}
                        >
                            <div className="flex items-center justify-between">
                                <BrainCircuit className={active ? "text-cyan-400" : "text-slate-400"} size={22} />
                                {unavailable
                                    ? <LockKeyhole className="text-slate-500" size={18} />
                                    : active && <CheckCircle2 className="text-cyan-400" size={18} />}
                            </div>
                            <div className="mt-3 font-semibold">{model.name}</div>
                            <div className="mt-1 text-xs text-slate-400">
                                {unavailable ? "Checkpoint required" : model.version}
                            </div>
                        </button>
                    );
                })}
            </div>
        </Card>
    );
}
