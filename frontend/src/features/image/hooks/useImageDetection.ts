import { useCallback, useEffect, useState } from "react";

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

export function useImageDetection() {

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

    const loadRecent = useCallback(async () => {

        try {

            const response = await getRecentDetection();

            setRecent(response);

        }

        catch (error) {

            console.error("Recent Detection Error:", error);

        }

    }, []);

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

        try {

            setLoading(true);

            setError(null);

            const response = await analyzeImage(selectedFile, selectedModel);

            setResult(response);

            await loadRecent();

        }

        catch (error) {

            console.error(error);

            setError(getApiErrorMessage(error, "Image analysis failed."));

        }

        finally {

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
