import axios, {AxiosError} from 'axios';
import log from 'loglevel';
import useAuthStore from "../store/useAuthStore.ts";
import {StatusCodes} from 'http-status-codes';
import type {BaseErrorPayload, IApiErrorResponse} from "./exceptions/baseExceptions.ts";
import {toBaseError} from "./exceptions/exceptionFactory.ts";


log.setLevel(import.meta.env.DEV ? 'debug' : 'warn');

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

function isAuthStorageShape(value: unknown): value is { state: { token?: { access_token?: string } } } {
    return typeof value === 'object' && value != null && 'state' in value;
}

// --- REQUEST INTERCEPTOR ---
axiosInstance.interceptors.request.use(
    function (config) {
        // 1. Get the string from localStorage
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
            // 2. Parse the JSON (Zustand wraps it in a 'state' object)
            const parsed: unknown = JSON.parse(authStorage);
            if (isAuthStorageShape(parsed)) {
                const token = parsed.state.token?.access_token;
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
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

// --- RESPONSE INTERCEPTOR ---
axiosInstance.interceptors.response.use(
    (response) => {
        log.debug(response)
        return response
    },
    (error: unknown) => {
        if (axios.isAxiosError(error)) {
            log.debug("API Error Response: ", error.response?.data)

            const typedError = error as AxiosError<IApiErrorResponse>;
            // No retry on 401: clear auth state so the UI falls back to the Login button.
            if (typedError.response?.status === StatusCodes.UNAUTHORIZED) {
                useAuthStore.getState().logout();
            }
            const backendErrorPayload: BaseErrorPayload | undefined = typedError.response?.data?.error;
            return Promise.reject(toBaseError(backendErrorPayload));
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;