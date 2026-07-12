import { useCallback, useEffect, useState } from "react";

import {
    analyzeImage,
    downloadReport,
} from "../services/image.service";

import { validateImage } from "../utils/fileValidation";

import { getRecentDetection } from "../../../services/dashboard.service";

import { downloadFile } from "../utils/downloadFile";

import type { ImageDetectionResponse } from "../../../types/image";
import type { RecentDetection } from "../../../types/dashboard";

export function useImageDetection() {

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const [preview, setPreview] = useState<string | null>(null);

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

    }, [loadRecent]);

    useEffect(() => {

        return () => {

            if (preview) {

                URL.revokeObjectURL(preview);

            }

        };

    }, [preview]);

    function selectImage(file: File) {

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

        setError(null);

    }

    async function detectImage() {

        if (!selectedFile) {

            setError("Please select an image.");

            return;

        }

        try {

            setLoading(true);

            setError(null);

            const response = await analyzeImage(selectedFile);

            console.log("IMAGE RESPONSE");
            console.dir(response, { depth: null });

            console.log("Prediction:", response.prediction);
            console.log("Model:", response.model);
            console.log("Confidence:", response.prediction?.confidence);

            setResult(response);

            await loadRecent();

        }

        catch (error) {

            console.error(error);

            setError("Image analysis failed.");

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

        setError(null);

    }

    function reset() {

        removeImage();

    }

    return {

        selectedFile,

        preview,

        result,

        recent,

        loading,

        error,

        hasResult: result !== null,

        selectImage,

        detectImage,

        handleDownloadReport,

        loadRecent,

        removeImage,

        reset,

    };

}