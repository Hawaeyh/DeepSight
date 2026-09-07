export function getApiErrorMessage(error: any, fallback: string): string {
    const detail = error?.response?.data?.detail;
    const safeMessages: Record<string, string> = {
        INVALID_FILE_TYPE: "Please upload a JPEG, PNG, or WEBP image.",
        FILE_TOO_LARGE: "The selected image is too large.",
        NO_FACE_DETECTED: "No clear face was detected in the image.",
        FACE_TOO_SMALL: "The detected face is too small for reliable analysis.",
        MODEL_UNAVAILABLE: "The detection model is currently unavailable.",
        INFERENCE_FAILED: "The image could not be analysed. Please try again.",
    };
    if (detail && typeof detail.code === "string" && safeMessages[detail.code]) return safeMessages[detail.code];
    if (typeof detail === "string") return detail;
    if (detail && typeof detail.message === "string") {
        if (!detail.plan) return detail.message;
        const reset = detail.resetsAt ? ` Resets ${new Date(detail.resetsAt).toLocaleString()}.` : "";
        return `${detail.message} Current plan: ${detail.plan}.${reset}`;
    }
    return error?.message || fallback;
}
