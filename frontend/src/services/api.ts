import axios from "axios";
import { getApiBaseUrl } from "./apiConfig";

type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | null = null;
let handlingUnauthorized = false;

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null) {
    unauthorizedHandler = handler;
}

export function resetUnauthorizedState() {
    handlingUnauthorized = false;
}

const api = axios.create({
    baseURL: getApiBaseUrl(),

    timeout: 60000,

    withCredentials: true,

    headers: {

        Accept: "application/json",

        "Content-Type": "application/json",

    },

});

api.interceptors.request.use(config => {
    const token = localStorage.getItem("deepsight-access-token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

let guestSessionRequest: Promise<void> | null = null;
let guestSessionReady = false;

export function ensureGuestSession(): Promise<void> {
    if (localStorage.getItem("deepsight-access-token")) return Promise.resolve();
    if (guestSessionReady) return Promise.resolve();
    if (!guestSessionRequest) {
        guestSessionRequest = axios.post(
            `${getApiBaseUrl()}/guest/session`,
            {},
            { withCredentials: true },
        ).then(() => { guestSessionReady = true; }).finally(() => { guestSessionRequest = null; });
    }
    return guestSessionRequest;
}

api.interceptors.response.use(

    response => response,

    error => {

        if (error.response?.status === 401) {
            const token = localStorage.getItem("deepsight-access-token");
            if (token && !handlingUnauthorized) {
                handlingUnauthorized = true;
                localStorage.removeItem("deepsight-access-token");
                unauthorizedHandler?.();
            }
            if (!token) guestSessionReady = false;
        }

        console.error(

            "API Error",

            error.response?.data ?? error.message,

        );

        return Promise.reject(error);

    },

);

export default api;
