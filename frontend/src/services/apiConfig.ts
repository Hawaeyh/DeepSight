const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";


export function getApiBaseUrl(environmentValue = import.meta.env.VITE_API_URL): string {
    const configured = environmentValue?.trim();
    return configured || DEFAULT_API_BASE_URL;
}
