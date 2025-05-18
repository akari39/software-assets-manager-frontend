// services/axiosConfig.js
import axios from 'axios';
import { globalSnackbarHandler } from '../components/GlobalSnackbar';

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL_DEV,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('jwt');
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  response => {
    console.log('Axios Response:', response);
    return response;
  },
  error => {
    const status = error.response?.status;
    if (status === 401) {
      // Clear tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jwt');
        localStorage.removeItem('employee_id');
      }
      if (globalSnackbarHandler) {
        globalSnackbarHandler({
          tip: '授权失败，请重新登录',
          type: 'error',
        });
      }
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin';
      }
      return Promise.resolve({ data: null, status: 401 });
    }

    if (globalSnackbarHandler) {
      globalSnackbarHandler(
        {
          tip: error.response?.data?.detail ||
            error.message ||
            '发生了一个错误',
          type: 'error',
        }
      );
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
