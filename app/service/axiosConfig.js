// services/axiosConfig.js
import axios from 'axios';

let globalErrorHandler = null;

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
      const token = localStorage.getItem('token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => {
    console.log('Axios response', response);
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.error('Unauthorized! Redirecting to login...');
      // You could call globalErrorHandler here if set.
      if (globalErrorHandler) globalErrorHandler("授权失败，请重新登录");
    } else {
      if (globalErrorHandler) globalErrorHandler(error.message || "发生了一个错误");
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
