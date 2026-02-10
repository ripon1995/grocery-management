import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// TODO => Add interceptors to handle error or auth token
// axiosInstance.interceptors.response.use(
//     (response) => response,
//     (error) => {
//         console.error('API Error:', error.response?.data || error.message);
//         return Promise.reject(error);
//     }
// );

export default axiosInstance;