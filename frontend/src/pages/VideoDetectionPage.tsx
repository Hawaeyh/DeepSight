import { useEffect, useRef, useState } from "react";
import { useDropzone } from "react-dropzone";

import { AuthenticatedImage } from "../components/auth/AuthenticatedImage";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import ProgressBar from "../components/ui/ProgressBar";
import api from "../services/api";
import type { VideoFrameResult, VideoJob, VideoSegment, VideoTrack } from "../types/video";
import { getApiErrorMessage } from "../utils/apiError";


export default function VideoDetectionPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [job, setJob] = useState<VideoJob | null>(null);
    const [frames, setFrames] = useState<VideoFrameResult[]>([]);
    const [tracks, setTracks] = useState<VideoTrack[]>([]);
    const [segments, setSegments] = useState<VideoSegment[]>([]);
    const [error, setError] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const jobId = job?.job_id;
    const jobStatus = job?.status;

    useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);
    useEffect(() => {
        if (!jobId || !jobStatus || !["pending", "queued", "processing", "cancel_requested"].includes(jobStatus)) return;
        const timer = window.setInterval(async () => {
            try {
                const response = await api.get<VideoJob>(`/videos/${jobId}/status`);
                setJob(response.data);
                if (response.data.status === "completed") {
                    const [frameResponse, trackResponse, segmentResponse] = await Promise.all([api.get<VideoFrameResult[]>(`/videos/${jobId}/frames`), api.get<VideoTrack[]>(`/videos/${jobId}/tracks`), api.get<VideoSegment[]>(`/videos/${jobId}/segments`)]);
                    setFrames(frameResponse.data); setTracks(trackResponse.data); setSegments(segmentResponse.data);
                }
            } catch (requestError) {
                setError(getApiErrorMessage(requestError, "Unable to refresh video progress."));
            }
        }, 1500);
        return () => window.clearInterval(timer);
    }, [jobId, jobStatus]);

    const dropzone = useDropzone({
        accept: { "video/mp4": [], "video/webm": [], "video/quicktime": [] }, multiple: false,
        maxSize: 100 * 1024 * 1024,
        onDrop: accepted => {
            if (preview) URL.revokeObjectURL(preview);
            const selected = accepted[0] ?? null;
            setFile(selected); setPreview(selected ? URL.createObjectURL(selected) : null);
            setJob(null); setFrames([]); setTracks([]); setSegments([]); setError(selected ? null : "Choose an MP4, MOV, or WebM file up to 100 MB.");
        },
    });

    async function submit() {
        if (!file) return;
        const data = new FormData(); data.append("file", file);
        try {
            setError(null);
            const response = await api.post<VideoJob>("/videos", data, { headers: { "Content-Type": "multipart/form-data" }, timeout: 120000 });
            setJob(response.data);
        } catch (requestError) { setError(getApiErrorMessage(requestError, "Video upload failed.")); }
    }

    async function cancel() {
        if (!job) return;
        const response = await api.post<VideoJob>(`/videos/${job.job_id}/cancel`);
        setJob(response.data);
    }

    async function removeJob() {
        if (!job) return;
        try {
            await api.delete(`/videos/${job.job_id}`);
            setJob(null); setFrames([]); setTracks([]); setSegments([]);
        } catch (requestError) { setError(getApiErrorMessage(requestError, "Unable to delete the video analysis.")); }
    }

    async function downloadReport() {
        if (!job) return;
        try {
            const response = await api.get(`/reports/${job.analysis_id}`, { responseType: "blob" });
            const url = URL.createObjectURL(response.data);
            const anchor = document.createElement("a"); anchor.href = url; anchor.download = `deepsight-analysis-${job.analysis_id}.pdf`; anchor.click();
            URL.revokeObjectURL(url);
        } catch (requestError) { setError(getApiErrorMessage(requestError, "Unable to create the report.")); }
    }

    function seek(timestampMs: number) {
        if (videoRef.current) videoRef.current.currentTime = timestampMs / 1000;
    }

    const active = job && ["pending", "queued", "processing", "cancel_requested"].includes(job.status);
    return <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Video Detection</h1><p className="mt-2 text-slate-400">Upload privately, then follow representative-frame analysis without blocking the page.</p></div>
        {error && <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-300">{error}</div>}
        <Card title="Upload Video" subtitle="MP4, MOV, or WebM · maximum 100 MB and 120 seconds">
            <div {...dropzone.getRootProps()} className="cursor-pointer rounded-lg border-2 border-dashed border-slate-700 p-8 text-center hover:border-cyan-500"><input {...dropzone.getInputProps()} />{file ? file.name : "Drop a video or click to browse"}</div>
            {preview && <video ref={videoRef} src={preview} controls className="mt-4 max-h-80 w-full bg-black" />}
            <div className="mt-4 flex gap-3"><Button onClick={submit} disabled={!file || Boolean(active)}>Queue Analysis</Button>{active && <Button variant="danger" onClick={cancel}>Cancel</Button>}</div>
        </Card>
        {job && <Card title={job.metadata?.display_label ?? job.status.replaceAll("_", " ")} subtitle={job.stage}>
            <ProgressBar value={job.progress} />
            <div className="mt-3 flex flex-wrap gap-5 text-sm text-slate-300"><span>{job.progress}%</span><span>{job.processed_frames}/{job.selected_frames} frames</span><span>{job.detected_tracks} face tracks</span>{job.overall_confidence !== null && <span>{job.overall_confidence.toFixed(1)}% confidence</span>}</div>
            {job.metadata?.sampling_notice && <p className="mt-4 text-sm text-slate-400">{job.metadata.sampling_notice}</p>}
            {job.error_message && <p className="mt-4 text-red-300">{job.error_code}: {job.error_message}</p>}
            {["completed", "failed", "cancelled"].includes(job.status) && <div className="mt-4 flex gap-3">{job.status === "completed" && <Button variant="secondary" onClick={downloadReport}>Download Report</Button>}<Button variant="danger" onClick={removeJob}>Delete</Button></div>}
        </Card>}
        {tracks.length > 0 && <Card title="Face tracks and suspicious segments" subtitle="Track IDs are local to this sampled video and are not biometric identities"><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{tracks.map(track => <div key={track.id} className="rounded border border-slate-700 p-3 text-sm"><strong>Track {track.track_number}</strong><div>{track.overall_result.replaceAll("_", " ")} · {track.overall_confidence.toFixed(1)}%</div><div className="text-slate-400">{track.frame_count} frames · {track.suspicious_frame_count} suspicious</div></div>)}</div>{segments.length > 0 && <div className="mt-4 flex flex-wrap gap-2">{segments.map(segment => <button key={segment.id} onClick={() => seek(segment.start_timestamp_ms)} className="rounded border border-red-500/40 px-3 py-2 text-sm text-red-200">Suspicious {(segment.start_timestamp_ms/1000).toFixed(1)}–{(segment.end_timestamp_ms/1000).toFixed(1)}s · {segment.confidence.toFixed(1)}%</button>)}</div>}</Card>}
        {frames.length > 0 && <Card title="Sampled timeline" subtitle="Select a labelled point to seek the local preview">
            <div className="mb-5 flex h-12 items-end gap-1" role="list" aria-label="Analysed video frames">{frames.map(frame => <button key={frame.id} role="listitem" aria-label={`${frame.prediction} at ${(frame.timestamp_ms/1000).toFixed(1)} seconds`} title={`${frame.prediction} · ${frame.fake_probability.toFixed(1)}% fake`} onClick={() => seek(frame.timestamp_ms)} className={`min-w-2 flex-1 rounded-t ${frame.prediction === "Fake" ? "bg-red-500" : "bg-emerald-500"}`} style={{height:`${Math.max(20,frame.confidence)}%`}} />)}</div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{frames.map(frame => <button key={frame.id} onClick={() => seek(frame.timestamp_ms)} className="overflow-hidden rounded-lg border border-slate-700 text-left"><AuthenticatedImage endpoint={frame.thumbnail_url} alt={`${frame.prediction} sampled frame`} className="aspect-video w-full object-cover" /><div className="p-3 text-sm"><strong>{frame.prediction}</strong> · {(frame.timestamp_ms/1000).toFixed(1)}s<br/><span className="text-slate-400">Track {frame.track_id} · {frame.sampling_reason}</span></div></button>)}</div>
        </Card>}
    </div>;
}
