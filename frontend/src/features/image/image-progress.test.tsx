import { act, fireEvent, render, renderHook, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { analyse, models, recent, metadata } = vi.hoisted(() => ({
    analyse: vi.fn(),
    models: vi.fn(() => Promise.resolve({ models: [{ key: "efficientnet", name: "EfficientNet", version: "1", description: "", available: true }] })),
    recent: vi.fn(() => Promise.resolve([])),
    metadata: vi.fn(() => Promise.resolve({ filename: "face.png", extension: "PNG", mimeType: "image/png", fileSize: 3, formattedFileSize: "3 B", width: 160, height: 160, resolution: "160 x 160", aspectRatio: "1:1", orientation: "Square", uploadTime: "now" })),
}));

vi.mock("./services/image.service", () => ({ analyzeImage: analyse, downloadReport: vi.fn(), getDetectionModels: models }));
vi.mock("../../services/dashboard.service", () => ({ getRecentDetection: recent }));
vi.mock("./utils/imageMetadata", () => ({ getImageMetadata: metadata }));
vi.mock("../../hooks/useAuth", () => ({ useAuth: () => ({ authStatus: "unauthenticated" }) }));

import ActionBar from "./components/ActionBar";
import AnalysisProgress from "./components/AnalysisProgress";
import { useImageDetection } from "./hooks/useImageDetection";

const completedResult = {
    id: 1, filename: "face.png", file_type: "Image", source: "web", file_extension: ".png", file_size: 1,
    prediction: "Real" as const, confidence: 91, real_probability: 91, fake_probability: 9, deepfake_type: null,
    type_confidence: null, risk_level: "Low" as const, model_name: "EfficientNet", model_version: "1", device: "cpu",
    processing_time: 1, status: "Completed", face_detected: true, face_count: 1, image_width: 160, image_height: 160,
    video_duration: null, frames_analyzed: null, fake_frames: null, real_frames: null, verified_result: null, remarks: null,
    created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z", quality_warnings: [],
};

describe("image analysis progress", () => {
    beforeEach(() => {
        vi.useFakeTimers();
        analyse.mockReset(); models.mockClear(); recent.mockClear(); metadata.mockClear();
        localStorage.clear();
        vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:preview"), revokeObjectURL: vi.fn() });
    });
    afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

    async function selectedHook() {
        const hook = renderHook(() => useImageDetection());
        const file = new File(["png"], "face.png", { type: "image/png" });
        await act(async () => { await hook.result.current.selectImage(file); });
        return hook;
    }

    it("starts below 100 percent and prevents duplicate submissions", async () => {
        let resolveRequest!: (value: typeof completedResult) => void;
        analyse.mockImplementationOnce(() => new Promise(resolve => { resolveRequest = resolve; }));
        const hook = await selectedHook();
        let request!: Promise<void>;
        act(() => { request = hook.result.current.detectImage(); void hook.result.current.detectImage(); });
        expect(analyse).toHaveBeenCalledTimes(1);
        expect(hook.result.current.loading).toBe(true);
        expect(hook.result.current.stage).toBe("uploading");
        expect(hook.result.current.progress).toBe(10);
        expect(hook.result.current.result).toBeNull();
        act(() => vi.advanceTimersByTime(3200));
        expect(hook.result.current.stage).toBe("analysing");
        expect(hook.result.current.progress).toBe(75);
        await act(async () => { resolveRequest(completedResult); await request; });
        expect(hook.result.current.stage).toBe("completed");
        expect(hook.result.current.progress).toBe(100);
        expect(hook.result.current.loading).toBe(false);
    });

    it("shows a safe failed state and permits retry", async () => {
        analyse.mockRejectedValueOnce({ response: { data: { detail: { code: "NO_FACE_DETECTED" } } } });
        const hook = await selectedHook();
        await act(async () => { await hook.result.current.detectImage(); });
        expect(hook.result.current.stage).toBe("failed");
        expect(hook.result.current.progress).toBeLessThan(100);
        expect(hook.result.current.error).toBe("No clear face was detected in the image.");
        expect(hook.result.current.loading).toBe(false);
        analyse.mockResolvedValueOnce(completedResult);
        await act(async () => { await hook.result.current.detectImage(); });
        expect(analyse).toHaveBeenCalledTimes(2);
        expect(hook.result.current.stage).toBe("completed");
    });

    it("clears the previous result when another analysis starts", async () => {
        analyse.mockResolvedValueOnce(completedResult);
        const hook = await selectedHook();
        await act(async () => { await hook.result.current.detectImage(); });
        expect(hook.result.current.result).toEqual(completedResult);
        analyse.mockImplementationOnce(() => new Promise(() => undefined));
        act(() => { void hook.result.current.detectImage(); });
        expect(hook.result.current.result).toBeNull();
        expect(hook.result.current.progress).toBeLessThan(100);
    });

    it("renders accessible status and disables controls while processing", () => {
        const onAnalyze = vi.fn();
        render(<><AnalysisProgress stage="analysing" progress={75} message="Running deepfake detection models..." /><ActionBar loading disabled={false} canDownload={false} completed={false} onAnalyze={onAnalyze} onDownload={vi.fn()} onReset={vi.fn()} onHistory={vi.fn()} onFeedback={vi.fn()} /></>);
        expect(screen.getByRole("status")).toHaveTextContent("Analysing Image");
        expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "75");
        const button = screen.getByRole("button", { name: "Analysing..." });
        expect(button).toBeDisabled();
        fireEvent.click(button);
        expect(onAnalyze).not.toHaveBeenCalled();
    });
});
