import { useEffect, useState } from "react";
import { CheckCircle2, ThumbsDown, ThumbsUp } from "lucide-react";

import api from "../../../services/api";
import Button from "../../../components/ui/Button";
import Card from "../../../components/ui/Card";
import type { ImageDetectionResponse } from "../types/image";
import { AI_MANIPULATIONS, DEEPFAKE_MANIPULATIONS } from "../utils/manipulation";

interface Props {
    result: ImageDetectionResponse;
}

type FakeCategory = "AI-generated" | "Deepfake";

export default function FeedbackPanel({ result }: Props) {
    const [correcting, setCorrecting] = useState(false);
    const [correctedPrediction, setCorrectedPrediction] = useState<"Real" | "Fake">(
        result.prediction === "Real" ? "Fake" : "Real",
    );
    const [fakeCategory, setFakeCategory] = useState<FakeCategory>("Deepfake");
    const [manipulation, setManipulation] = useState(DEEPFAKE_MANIPULATIONS[0]);
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setCorrecting(false);
        setCorrectedPrediction(result.prediction === "Real" ? "Fake" : "Real");
        setMessage(null);
        setError(null);
    }, [result.id, result.prediction]);

    useEffect(() => {
        setManipulation(
            fakeCategory === "AI-generated"
                ? AI_MANIPULATIONS[0]
                : DEEPFAKE_MANIPULATIONS[0],
        );
    }, [fakeCategory]);

    async function submit(isCorrect: boolean) {
        try {
            setSubmitting(true);
            setError(null);
            const response = await api.post<{ status: string; hardExamplePath: string | null }>("/feedback", {
                analysis_id: result.id,
                is_correct: isCorrect,
                corrected_prediction: isCorrect ? null : correctedPrediction,
                fake_category: !isCorrect && correctedPrediction === "Fake" ? fakeCategory : null,
                manipulation_type: !isCorrect && correctedPrediction === "Fake" ? manipulation : null,
            });
            setMessage(
                response.data.status === "queued_for_retraining"
                    ? "Correction saved. This image is queued as a hard example for retraining."
                    : "Prediction verified. Thank you for reviewing it.",
            );
            setCorrecting(false);
        }
        catch (requestError: any) {
            setError(requestError?.response?.data?.detail ?? "Unable to save feedback.");
        }
        finally {
            setSubmitting(false);
        }
    }

    return (
        <Card title="Review This Prediction" subtitle="Reviewer feedback improves future model versions">
            {message ? (
                <div className="flex items-start gap-3 rounded-lg bg-green-500/10 p-4 text-green-300">
                    <CheckCircle2 className="mt-0.5 shrink-0" size={20} />
                    <p>{message}</p>
                </div>
            ) : (
                <div className="space-y-5">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <p className="font-medium">Is the {result.prediction} prediction correct?</p>
                        <div className="flex gap-3">
                            <Button onClick={() => submit(true)} disabled={submitting}><ThumbsUp className="mr-2 inline" size={18} />Yes</Button>
                            <Button variant="danger" onClick={() => setCorrecting(true)} disabled={submitting}><ThumbsDown className="mr-2 inline" size={18} />No</Button>
                        </div>
                    </div>

                    {correcting && (
                        <div className="space-y-4 border-t border-slate-700 pt-5">
                            <label className="block"><span className="mb-2 block text-sm text-slate-400">What is the correct result?</span><select value={correctedPrediction} onChange={event => setCorrectedPrediction(event.target.value as "Real" | "Fake")} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3"><option value="Real">Real / authentic</option><option value="Fake">Fake / manipulated</option></select></label>
                            {correctedPrediction === "Fake" && (
                                <>
                                    <label className="block"><span className="mb-2 block text-sm text-slate-400">Fake category</span><select value={fakeCategory} onChange={event => setFakeCategory(event.target.value as FakeCategory)} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3"><option value="AI-generated">AI-generated</option><option value="Deepfake">Deepfake</option></select></label>
                                    <label className="block"><span className="mb-2 block text-sm text-slate-400">Manipulation type</span><select value={manipulation} onChange={event => setManipulation(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3">{(fakeCategory === "AI-generated" ? AI_MANIPULATIONS : DEEPFAKE_MANIPULATIONS).map(item => <option key={item}>{item}</option>)}</select></label>
                                </>
                            )}
                            <div className="flex gap-3"><Button onClick={() => submit(false)} disabled={submitting}>{submitting ? "Saving..." : "Submit Correction"}</Button><Button variant="secondary" onClick={() => setCorrecting(false)}>Cancel</Button></div>
                        </div>
                    )}
                    {error && <p className="rounded-lg bg-red-500/10 p-3 text-red-300">{error}</p>}
                </div>
            )}
        </Card>
    );
}
