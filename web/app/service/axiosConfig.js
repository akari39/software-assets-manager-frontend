// services/axiosConfig.js
import axios from 'axios';
import { redirect } from 'next/navigation';

export let globalErrorHandler = null;
export function setGlobalErrorHandler(handler) {
  globalErrorHandler = handler;
}

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
  response => response,
  error => {
    const status = error.response?.status;
    if (status === 401) {
      // Clear tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jwt');
        localStorage.removeItem('employee_id');
      }
      if (globalErrorHandler) {
        globalErrorHandler('授权失败，请重新登录');
      }
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin';
      }
      return Promise.resolve({ data: null, status: 401 });
    }

    if (globalErrorHandler) {
      globalErrorHandler(
        error.response?.data?.detail ||
        error.message ||
        '发生了一个错误'
      );
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
