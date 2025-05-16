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
      const token = localStorage.getItem('token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt');
      localStorage.removeItem('employee_id');
      redirect('/auth/signin');
    }
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => {
    console.log('Axios response', response);
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.error('Unauthorized! Redirecting to login...');
      if (globalErrorHandler) globalErrorHandler("授权失败，请重新登录");
    } else {
      if (globalErrorHandler) globalErrorHandler(error.response.data.detail || error.message || "发生了一个错误");
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
