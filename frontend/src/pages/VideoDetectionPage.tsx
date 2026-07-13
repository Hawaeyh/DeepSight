import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Download, Film, RotateCcw, ShieldAlert, ShieldCheck, UploadCloud } from "lucide-react";

import api from "../services/api";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import ProgressBar from "../components/ui/ProgressBar";
import { downloadFile } from "../features/image/utils/downloadFile";
import type { VideoDetectionResponse } from "../types/video";
import { getApiErrorMessage } from "../utils/apiError";

export default function VideoDetectionPage() {
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<VideoDetectionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const dropzone = useDropzone({
        accept: { "video/mp4": [], "video/webm": [], "video/quicktime": [] },
        multiple: false,
        maxSize: 250 * 1024 * 1024,
        onDrop: accepted => {
            setFile(accepted[0] ?? null);
            setResult(null);
            setError(accepted.length ? null : "Choose an MP4, WebM, or MOV file up to 250 MB.");
        },
    });

    async function analyze() {
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        try {
            setLoading(true);
            setError(null);
            const response = await api.post<VideoDetectionResponse>("/video/analyze", formData, {
                headers: { "Content-Type": "multipart/form-data" },
                timeout: 10 * 60 * 1000,
            });
            setResult(response.data);
        }
        catch (requestError: any) {
            setError(getApiErrorMessage(requestError, "Video analysis failed."));
        }
        finally {
            setLoading(false);
        }
    }

    async function downloadReport() {
        if (!result) return;
        const response = await api.get(`/reports/${result.id}`, { responseType: "blob" });
        downloadFile(response.data, `Video_Analysis_${result.id}.pdf`);
    }

    function reset() {
        setFile(null);
        setResult(null);
        setError(null);
    }

    const analyzedFrames = result?.frames_analyzed ?? 0;
    const fakeFramePercentage = analyzedFrames
        ? ((result?.fake_frames ?? 0) / analyzedFrames) * 100
        : 0;

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Video Detection</h1>
                <p className="mt-2 text-slate-400">Analyze sampled frames for deepfake manipulation.</p>
            </div>

            {error && <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-300">{error}</div>}

            <Card title="Upload Video" subtitle="MP4, WebM, or MOV up to 250 MB">
                <div
                    {...dropzone.getRootProps()}
                    className={`cursor-pointer rounded-lg border-2 border-dashed p-10 text-center transition ${
                        dropzone.isDragActive ? "border-cyan-400 bg-cyan-500/10" : "border-slate-700 hover:border-cyan-500"
                    }`}
                >
                    <input {...dropzone.getInputProps()} />
                    {file ? <Film className="mx-auto text-green-400" size={58} /> : <UploadCloud className="mx-auto text-cyan-400" size={58} />}
                    <h2 className="mt-4 text-lg font-semibold">{file?.name ?? "Drop a video or click to browse"}</h2>
                    {file && <p className="mt-2 text-sm text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>}
                </div>
                <div className="mt-5 flex flex-wrap gap-3">
                    <Button onClick={analyze} disabled={!file || loading}>{loading ? "Analyzing video..." : "Analyze Video"}</Button>
                    <Button variant="secondary" onClick={downloadReport} disabled={!result}><Download className="mr-2 inline" size={18} />Download Report</Button>
                    <Button variant="danger" onClick={reset}><RotateCcw className="mr-2 inline" size={18} />Reset</Button>
                </div>
            </Card>

            {result && (
                <>
                <div className="grid gap-6 xl:grid-cols-2">
                    <Card title="Detection Result" subtitle={`Analysis #${result.id}`}>
                        <div className="flex items-center gap-4">
                            {result.prediction === "Fake"
                                ? <ShieldAlert className="text-red-400" size={58} />
                                : <ShieldCheck className="text-green-400" size={58} />}
                            <div>
                                <div className="text-3xl font-bold">{result.prediction}</div>
                                <div className="mt-1 text-slate-400">{result.confidence.toFixed(2)}% confidence</div>
                            </div>
                        </div>
                        <div className="mt-7 space-y-3 text-sm">
                            <div className="flex justify-between"><span className="text-slate-400">Duration</span><span>{(result.video_duration ?? 0).toFixed(1)} seconds</span></div>
                            <div className="flex justify-between"><span className="text-slate-400">Model</span><span>{result.model_name} {result.model_version}</span></div>
                            <div className="flex justify-between"><span className="text-slate-400">Processing time</span><span>{result.processing_time.toFixed(2)} seconds</span></div>
                        </div>
                    </Card>

                    <Card title="Frame Analysis" subtitle={`${analyzedFrames} sampled frames`}>
                        <div className="space-y-5">
                            <div><div className="mb-2 flex justify-between"><span>Fake frames</span><span>{result.fake_frames ?? 0}</span></div><ProgressBar value={fakeFramePercentage} /></div>
                            <div className="grid grid-cols-2 gap-4 text-center">
                                <div className="rounded-lg bg-red-500/10 p-4"><div className="text-2xl font-bold text-red-400">{result.fake_frames ?? 0}</div><div className="mt-1 text-sm text-slate-400">Fake</div></div>
                                <div className="rounded-lg bg-green-500/10 p-4"><div className="text-2xl font-bold text-green-400">{result.real_frames ?? 0}</div><div className="mt-1 text-sm text-slate-400">Real</div></div>
                            </div>
                        </div>
                    </Card>
                </div>
                <Card title="Video Summary" subtitle="Frame-level detection conclusion">
                    <p className="leading-7 text-slate-300">{result.summary}</p>
                </Card>
                <Card title="Analyzed Frames" subtitle="One sampled frame per second">
                    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                        {result.frame_results.map(frame => (
                            <article key={frame.index} className="overflow-hidden rounded-lg border border-slate-700 bg-slate-950">
                                <div className="aspect-video bg-slate-900">
                                    <img src={`http://127.0.0.1:8000${frame.thumbnail_url}`} alt={`Video frame at ${frame.timestamp.toFixed(1)} seconds`} className="h-full w-full object-cover" loading="lazy" />
                                </div>
                                <div className="p-3">
                                    <div className="flex items-center justify-between"><span className="text-sm text-slate-400">{frame.timestamp.toFixed(1)}s</span><span className={frame.prediction === "Fake" ? "font-semibold text-red-400" : "font-semibold text-green-400"}>{frame.prediction}</span></div>
                                    <div className="mt-2 text-xs text-slate-400">{frame.confidence.toFixed(1)}% confidence · Fake {frame.fake_probability.toFixed(1)}%</div>
                                </div>
                            </article>
                        ))}
                    </div>
                </Card>
                </>
            )}
        </div>
    );
}
