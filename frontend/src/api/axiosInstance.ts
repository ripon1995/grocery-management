import axios from 'axios';
import log from 'loglevel';


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
        const token = localStorage.getItem('token');

        // --- LOGGING WITH LOGLEVEL ---
        log.info(`%c[API REQUEST] ${config.method?.toUpperCase()} -> ${config.url}`, "color: #00ff00; font-weight: bold;");
        log.debug("Headers:", config.headers);
        if (config.data) log.debug("Body:", config.data);
        // ------------------------------
        // TODO => Add interceptors to handle error or auth token
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

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
        log.debug('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export default axiosInstance;