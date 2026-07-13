export function getApiErrorMessage(error: any, fallback: string): string {
    const detail = error?.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail.message === "string") {
        const reset = detail.resetsAt ? ` Resets ${new Date(detail.resetsAt).toLocaleString()}.` : "";
        return `${detail.message} Current plan: ${detail.plan}.${reset}`;
    }
    return error?.message || fallback;
}
