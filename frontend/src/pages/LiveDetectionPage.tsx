import { useEffect, useRef, useState } from "react";
import { Camera, CircleStop } from "lucide-react";

import api from "../services/api";

type LivePrediction = { prediction: "Real" | "Fake"; confidence: number; fake_probability: number; face_box?: number[]; frame_width: number; frame_height: number };

export default function LiveDetectionPage() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const sessionIdRef = useRef<string | null>(null);
    const analyzingRef = useRef(false);
    const predictionsRef = useRef<LivePrediction[]>([]);
    const lastSignatureRef = useRef<string | null>(null);
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState<LivePrediction | null>(null);
    const [face, setFace] = useState<LivePrediction | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [validFrames, setValidFrames] = useState(0);
    const [startedAt, setStartedAt] = useState<number | null>(null);
    const [seconds, setSeconds] = useState(0);
    const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
    const [cameraId, setCameraId] = useState("");

    useEffect(() => () => { stop(true); }, []);
    useEffect(() => { if (!running) return; const timer = window.setInterval(analyzeFrame, 1000); return () => window.clearInterval(timer); }, [running]);
    useEffect(() => { if (!running || !startedAt) return; const timer = window.setInterval(() => setSeconds(Math.floor((Date.now() - startedAt) / 1000)), 1000); return () => window.clearInterval(timer); }, [running, startedAt]);

    async function start() {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({ video: cameraId ? { deviceId: { exact: cameraId } } : { facingMode: "user", width: { min: 640 }, height: { min: 480 } }, audio: false });
            streamRef.current = stream;
            const session = await api.post<{sessionId:string}>("/webcam/sessions");
            sessionIdRef.current = session.data.sessionId;
            if (videoRef.current) videoRef.current.srcObject = stream;
            const devices = await navigator.mediaDevices.enumerateDevices(); setCameras(devices.filter(item => item.kind === "videoinput"));
            predictionsRef.current = []; lastSignatureRef.current = null; setResult(null); setFace(null); setValidFrames(0); setSeconds(0); setStartedAt(Date.now()); setRunning(true);
        } catch (requestError: any) {
            streamRef.current?.getTracks().forEach(track => track.stop()); streamRef.current = null;
            setError(requestError?.response?.data?.detail?.message ?? "Camera access was not granted or live detection is unavailable.");
        }
    }

    function stop(save = true) {
        const sessionId = sessionIdRef.current; sessionIdRef.current = null;
        streamRef.current?.getTracks().forEach(track => track.stop()); streamRef.current = null; analyzingRef.current = false; setRunning(false); setFace(null);
        if (save && sessionId) void api.post(`/webcam/sessions/${sessionId}/stop`).catch(() => undefined);
    }

    async function analyzeFrame() {
        const video = videoRef.current; const sessionId = sessionIdRef.current;
        if (!video || !sessionId || video.readyState < 2 || analyzingRef.current || document.hidden || video.paused) return;
        const sample = document.createElement("canvas"); sample.width = 16; sample.height = 16; sample.getContext("2d")?.drawImage(video, 0, 0, 16, 16);
        const signature = sample.toDataURL("image/jpeg", 0.25); if (signature === lastSignatureRef.current) return; lastSignatureRef.current = signature;
        analyzingRef.current = true;
        const canvas = document.createElement("canvas"); canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext("2d")?.drawImage(video, 0, 0);
        const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, "image/jpeg", 0.88));
        if (!blob) { analyzingRef.current = false; return; }
        const form = new FormData(); form.append("file", blob, "webcam-frame.jpg");
        try {
            const response = await api.post<LivePrediction>(`/webcam/sessions/${sessionId}/frames`, form, { headers: { "Content-Type": "multipart/form-data" } });
            const windowed = [...predictionsRef.current, response.data].slice(-7); predictionsRef.current = windowed; setFace(response.data); setValidFrames(value => value + 1);
            if (windowed.length >= 3) {
                const fake = windowed.filter(item => item.prediction === "Fake").length; const real = windowed.length - fake;
                if (Math.max(fake, real) >= Math.ceil(windowed.length * 0.65)) {
                    const stable = fake > real ? "Fake" : "Real"; const matching = windowed.filter(item => item.prediction === stable);
                    setResult({ ...response.data, prediction: stable, confidence: matching.reduce((sum, item) => sum + item.confidence, 0) / matching.length });
                }
            }
            setError(null);
        } catch (requestError: any) {
            const code = requestError?.response?.data?.detail?.code;
            if (!new Set(["NO_FACE_DETECTED", "QUALITY_TOO_LOW"]).has(code)) setError(requestError?.response?.data?.detail?.message ?? "Live analysis failed.");
            if ([401,403,409].includes(requestError?.response?.status)) stop();
        } finally { analyzingRef.current = false; }
    }

    const box = face?.face_box;
    return <div className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-medium text-cyan-400">Private sampled session</p><h1 className="mt-1 text-3xl font-bold">Live Detection</h1><p className="mt-1 text-sm text-slate-400">{running ? `${seconds}s · ${validFrames} valid frames · connected` : "Frames are temporary; only one final session summary is stored."}</p></div><div className="flex gap-2">{!running && cameras.length > 1 && <select aria-label="Camera" value={cameraId} onChange={event => setCameraId(event.target.value)} className="rounded-lg bg-slate-900 px-3"><option value="">Default camera</option>{cameras.map(item => <option key={item.deviceId} value={item.deviceId}>{item.label || "Camera"}</option>)}</select>}{running ? <button onClick={() => stop()} className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 font-semibold"><CircleStop size={19}/>Stop</button> : <button onClick={start} className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 font-semibold"><Camera size={19}/>Start Camera</button>}</div></div>
        {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>}
        <div className="relative min-h-[55vh] overflow-hidden bg-black"><video ref={videoRef} autoPlay muted playsInline className="h-full min-h-[55vh] w-full object-contain"/>{box && face && <div aria-label="Detected face" className="pointer-events-none absolute border-2 border-cyan-400" style={{left:`${box[0]/face.frame_width*100}%`,top:`${box[1]/face.frame_height*100}%`,width:`${(box[2]-box[0])/face.frame_width*100}%`,height:`${(box[3]-box[1])/face.frame_height*100}%`}}/>}{!running && <div className="absolute inset-0 flex items-center justify-center text-slate-500">Camera is off</div>}{running && <div className={`absolute left-4 top-4 rounded-lg px-4 py-3 text-lg font-bold ${!result ? "bg-slate-700" : result.prediction === "Fake" ? "bg-red-600" : "bg-emerald-600"}`}>{result ? `${result.prediction === "Fake" ? "Likely Manipulated" : "Likely Real"} · ${result.confidence.toFixed(1)}%` : "Analysing…"}</div>}</div>
    </div>;
}
