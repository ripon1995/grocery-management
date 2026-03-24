import axios from 'axios';
import log from 'loglevel';
import {BaseError, type BaseErrorResponse} from "./types/common.ts";


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
    (error) => {
        log.debug(error.response.data)
        const error_params: BaseErrorResponse = {
            status: error.response.data.status,
            error_code: error.response.data.error_code,
            message: error.response.data.message,
            detail: error.response.data.detail
        }
        return Promise.reject(new BaseError(error_params));
    }
);

export default axiosInstance;