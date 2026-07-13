import axios from "axios";

const api = axios.create({

    baseURL: "http://127.0.0.1:8000/api/v1",

    timeout: 60000,

    headers: {

        Accept: "application/json",

        "Content-Type": "application/json",

    },

});

function getGuestId() {
    let guestId = localStorage.getItem("deepsight-guest-id");
    if (!guestId) {
        guestId = crypto.randomUUID();
        localStorage.setItem("deepsight-guest-id", guestId);
    }
    return guestId;
}

api.interceptors.request.use(config => {
    const token = localStorage.getItem("deepsight-access-token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    config.headers["X-Guest-ID"] = getGuestId();
    return config;
});

api.interceptors.response.use(

    response => response,

    error => {

        console.error(

            "API Error",

            error.response?.data ?? error.message,

        );

        return Promise.reject(error);

    },

);

export default api;
