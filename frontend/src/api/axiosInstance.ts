import axios from 'axios';
import log from 'loglevel';
import {BaseError} from "./types/common.ts";
import useAuthStore from "../store/useAuthStore.ts";
import {StatusCodes} from 'http-status-codes';


log.setLevel(import.meta.env.DEV ? 'debug' : 'warn');

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

axiosInstance.interceptors.request.use(
    function (config) {
        // 1. Get the string from localStorage
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
            // 2. Parse the JSON (Zustand wraps it in a 'state' object)
            const parsedStorage = JSON.parse(authStorage);
            const token = parsedStorage.state.token?.access_token;
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        // --- LOGGING WITH LOGLEVEL ---
        log.info(`%c[API REQUEST] ${config.method?.toUpperCase()} -> ${config.url}`, "color: #00ff00; font-weight: bold;");
        log.debug("Headers:", config.headers);
        if (config.data) log.debug("Body:", config.data);

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);


axiosInstance.interceptors.response.use(
    (response) => {
        log.debug(response)
        return response
    },
    (error: unknown) => {
        if (axios.isAxiosError(error)) {
            log.debug("API Error Response: ", error.response?.data)

            // No retry on 401: clear auth state so the UI falls back to the Login button.
            if (error.response?.status === StatusCodes.UNAUTHORIZED) {
                useAuthStore.getState().logout();
            }
            return Promise.reject(new BaseError(error.response?.data));
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;