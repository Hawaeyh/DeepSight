import {

    useCallback,

    useEffect,

    useState,

} from "react";

import {

    analyzeImage,

    downloadReport,

} from "../services/image.service";

import {

    validateImage,

} from "../utils/fileValidation";

import {

    downloadFile,

} from "../utils/downloadFile";

import {

    getRecentDetection,

} from "../../../services/dashboard.service";

import {

    getImageMetadata,

} from "../utils/imageMetadata";

import type {

    ImageDetectionResponse,

} from "../types/image";

import type {

    ImageMetadata,

} from "../types/metadata";

import type {

    RecentDetection,

} from "../../../types/dashboard";

export function useImageDetection() {

    const [

        selectedFile,

        setSelectedFile,

    ] = useState<File | null>(null);

    const [

        preview,

        setPreview,

    ] = useState<string | null>(null);

    const [

        metadata,

        setMetadata,

    ] = useState<ImageMetadata | null>(null);

    const [

        result,

        setResult,

    ] = useState<ImageDetectionResponse | null>(null);

    const [

        recent,

        setRecent,

    ] = useState<RecentDetection[]>([]);

    const [

        loading,

        setLoading,

    ] = useState(false);

    const [

        error,

        setError,

    ] = useState<string | null>(null);

    const loadRecent = useCallback(async () => {

        try {

            const response =

                await getRecentDetection();

            setRecent(response);

        }

        catch (error) {

            console.error(

                "Recent Detection Error:",

                error

            );

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

    async function selectImage(file: File) {

        const validation =

            validateImage(file);

        if (validation) {

            setError(validation);

            return;

        }

        if (preview) {

            URL.revokeObjectURL(preview);

        }

        const objectUrl =

            URL.createObjectURL(file);

        setSelectedFile(file);

        setPreview(objectUrl);

        setResult(null);

        setError(null);

        try {

            const info =

                await getImageMetadata(file);

            setMetadata(info);

        }

        catch (error) {

            console.error(error);

        }

    }

    async function detectImage() {

        if (!selectedFile) {

            setError(

                "Please select an image."

            );

            return;

        }

        try {

            setLoading(true);

            setError(null);

            const response =

                await analyzeImage(

                    selectedFile

                );

            setResult(response);

            await loadRecent();

        }

        catch (error) {

            console.error(error);

            setError(

                "Image analysis failed."

            );

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

            const pdf =

                await downloadReport(

                    result.analysisId

                );

            downloadFile(

                pdf,

                `Analysis_${result.analysisId}.pdf`

            );

        }

        catch (error) {

            console.error(error);

            setError(

                "Unable to download report."

            );

        }

    }

    function removeImage() {

        if (preview) {

            URL.revokeObjectURL(preview);

        }

        setSelectedFile(null);

        setPreview(null);

        setMetadata(null);

        setResult(null);

        setError(null);

    }

    function reset() {

        removeImage();

    }

    return {

        selectedFile,

        preview,

        metadata,

        result,

        recent,

        loading,

        error,

        hasResult: result !== null,

        selectImage,

        detectImage,

        handleDownloadReport,

        removeImage,

        reset,

        loadRecent,

    };

}