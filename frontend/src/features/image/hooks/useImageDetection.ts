import { useCallback, useEffect, useRef, useState } from "react";

import {
    analyzeImage,
    downloadReport,
    getDetectionModels,
} from "../services/image.service";

import { validateImage } from "../utils/fileValidation";

import { getRecentDetection } from "../../../services/dashboard.service";

import { downloadFile } from "../utils/downloadFile";
import { getImageMetadata } from "../utils/imageMetadata";

import type { ImageDetectionResponse } from "../types/image";
import type { ImageMetadata } from "../types/metadata";
import type { RecentDetection } from "../../../types/dashboard";
import type { DetectionModel, ModelKey } from "../../../types/model";
import { getApiErrorMessage } from "../../../utils/apiError";
import { useAuth } from "../../../hooks/useAuth";
import type { AnalysisStage } from "../components/AnalysisProgress";

export function useImageDetection() {

    const { authStatus } = useAuth();

    const storedModel = localStorage.getItem("deepsight-default-model") as ModelKey | null;

    const [selectedModel, setSelectedModelState] = useState<ModelKey>(
        storedModel ?? "efficientnet",
    );

    const [models, setModels] = useState<DetectionModel[]>([]);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const [preview, setPreview] = useState<string | null>(null);

    const [metadata, setMetadata] = useState<ImageMetadata | null>(null);

    const [result, setResult] =
        useState<ImageDetectionResponse | null>(null);

    const [recent, setRecent] =
        useState<RecentDetection[]>([]);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);
    const [stage, setStage] = useState<AnalysisStage>("idle");
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState("Select an image when you are ready.");
    const inFlight = useRef(false);
    const stageTimers = useRef<number[]>([]);

    const clearStageTimers = useCallback(() => {
        stageTimers.current.forEach(timer => window.clearTimeout(timer));
        stageTimers.current = [];
    }, []);

    useEffect(() => clearStageTimers, [clearStageTimers]);

    const loadRecent = useCallback(async () => {

        if (authStatus !== "authenticated") {
            setRecent([]);
            return;
        }

        try {

            const response = await getRecentDetection();

            setRecent(response);

        }

        catch (error) {

            console.error("Recent Detection Error:", error);

        }

    }, [authStatus]);

    useEffect(() => {

        loadRecent();

        getDetectionModels()
            .then(({ models: availableModels }) => {
                setModels(availableModels);
                const current = availableModels.find(item => item.key === selectedModel);
                if (!current?.available) {
                    const fallback = availableModels.find(item => item.available);
                    if (fallback) {
                        setSelectedModelState(fallback.key);
                    }
                }
            })
            .catch(() => setError("Unable to load the model catalog."));

    }, [loadRecent, selectedModel]);

    function setSelectedModel(model: ModelKey) {
        setSelectedModelState(model);
        localStorage.setItem("deepsight-default-model", model);
        setResult(null);
    }

    useEffect(() => {

        return () => {

            if (preview) {

                URL.revokeObjectURL(preview);

            }

        };

    }, [preview]);

    async function selectImage(file: File) {

        const validation = validateImage(file);

        if (validation) {

            setError(validation);

            return;

        }

        if (preview) {

            URL.revokeObjectURL(preview);

        }

        const objectURL = URL.createObjectURL(file);

        setSelectedFile(file);

        setPreview(objectURL);

        setResult(null);

        setMetadata(null);

        setError(null);
        setStage("ready");
        setProgress(0);
        setProgressMessage("Image selected and ready to analyse.");

        try {
            setMetadata(await getImageMetadata(file));
        }
        catch {
            setError("Unable to read image metadata.");
        }

    }

    async function detectImage() {

        if (!selectedFile) {

            setError("Please select an image.");

            return;

        }

        if (inFlight.current) return;

        try {

            inFlight.current = true;

            setLoading(true);

            setError(null);

            setResult(null);
            clearStageTimers();
            setStage("uploading");
            setProgress(10);
            setProgressMessage("Preparing your image for secure upload...");
            const estimatedStages: Array<[number, AnalysisStage, number, string]> = [
                [400, "validating", 25, "Validating image quality and format..."],
                [1000, "detecting-face", 40, "Detecting facial regions..."],
                [1900, "loading-model", 55, "Preparing the configured detection model..."],
                [3000, "analysing", 75, "Running deepfake detection models..."],
                [5000, "saving", 90, "Waiting for the server to prepare your result..."],
            ];
            stageTimers.current = estimatedStages.map(([delay, nextStage, nextProgress, message]) => window.setTimeout(() => {
                if (!inFlight.current) return;
                setStage(nextStage); setProgress(nextProgress); setProgressMessage(message);
            }, delay));

            const response = await analyzeImage(selectedFile, selectedModel);

            clearStageTimers();

            setResult(response);

            setStage("completed");
            setProgress(100);
            setProgressMessage("Analysis completed successfully.");

            await loadRecent();

        }

        catch (error) {

            clearStageTimers();

            console.error(error);

            setError(getApiErrorMessage(error, "Image analysis failed."));

            setStage("failed");
            setProgress(current => Math.min(current, 90));
            setProgressMessage("Analysis failed. Review the message and try again.");

        }

        finally {

            inFlight.current = false;
            setLoading(false);

        }

    }

    async function handleDownloadReport() {

        if (!result) {

            return;

        }

        try {

            const pdf = await downloadReport(
                result.id
            );

            downloadFile(
                pdf,
                `Analysis_${result.id}.pdf`
            );

        }

        catch (error) {

            console.error(error);

            setError("Unable to download report.");

        }

    }

    function removeImage() {

        if (preview) {

            URL.revokeObjectURL(preview);

        }

        setSelectedFile(null);

        setPreview(null);

        setResult(null);

        setMetadata(null);

        setError(null);
        setStage("idle");
        setProgress(0);
        setProgressMessage("Select an image when you are ready.");

    }

    function reset() {

        removeImage();

    }

    return {

        selectedFile,

        preview,

        metadata,

        models,

        selectedModel,

        result,

        recent,

        loading,

        error,

        stage,
        progress,
        progressMessage,

        hasResult: result !== null,

        selectImage,

        setSelectedModel,

        detectImage,

        handleDownloadReport,

        loadRecent,

        removeImage,

        reset,

    };

}
