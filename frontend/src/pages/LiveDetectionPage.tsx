import { useEffect, useRef, useState } from "react";
import { Camera, CircleStop } from "lucide-react";

import api from "../services/api";
import type { ImageDetectionResponse } from "../features/image/types/image";

export default function LiveDetectionPage() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const analyzingRef = useRef(false);
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState<ImageDetectionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => () => streamRef.current?.getTracks().forEach(track => track.stop()), []);

    useEffect(() => {
        if (!running) return;
        const timer = window.setInterval(analyzeFrame, 4000);
        return () => window.clearInterval(timer);
    }, [running]);

    async function start() {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
            streamRef.current = stream;
            if (videoRef.current) videoRef.current.srcObject = stream;
            setRunning(true);
        } catch {
            setError("Camera access was not granted.");
        }
    }

    function stop() {
        streamRef.current?.getTracks().forEach(track => track.stop());
        streamRef.current = null;
        setRunning(false);
    }

    async function analyzeFrame() {
        const video = videoRef.current;
        if (!video || video.readyState < 2 || analyzingRef.current) return;
        analyzingRef.current = true;
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d")?.drawImage(video, 0, 0);
        const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, "image/jpeg", 0.88));
        if (!blob) { analyzingRef.current = false; return; }
        const form = new FormData();
        form.append("file", blob, `live-${Date.now()}.jpg`);
        form.append("model", "efficientnet");
        try {
            const response = await api.post<ImageDetectionResponse>("/analysis/image", form, { headers: { "Content-Type": "multipart/form-data", "X-DeepSight-Client": "live" } });
            setResult(response.data);
            setError(null);
        } catch (requestError: any) {
            setError(requestError?.response?.data?.detail ?? "Live analysis failed.");
            if (requestError?.response?.status === 403) stop();
        } finally {
            analyzingRef.current = false;
        }
    }

    return (
        <div className="space-y-5">
            <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-medium text-cyan-400">Lite</p><h1 className="mt-1 text-3xl font-bold">Live Detection</h1></div>{running ? <button onClick={stop} className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 font-semibold hover:bg-red-500"><CircleStop size={19} />Stop</button> : <button onClick={start} className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 font-semibold hover:bg-cyan-400"><Camera size={19} />Start Camera</button>}</div>
            {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-300">{typeof error === "string" ? error : JSON.stringify(error)}</div>}
            <div className="relative min-h-[55vh] overflow-hidden bg-black">
                <video ref={videoRef} autoPlay muted playsInline className="h-full min-h-[55vh] w-full object-contain" />
                {!running && <div className="absolute inset-0 flex items-center justify-center text-slate-500">Camera is off</div>}
                {result && running && <div className={`absolute left-4 top-4 rounded-lg px-4 py-3 text-lg font-bold shadow-xl ${result.prediction === "Fake" ? "bg-red-600" : "bg-emerald-600"}`}>{result.prediction} · {result.confidence.toFixed(1)}%</div>}
            </div>
        </div>
    );
}
