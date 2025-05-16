import axiosInstance, { globalErrorHandler } from '@/app/service/axiosConfig';
import { redirect } from 'next/navigation';

export async function signInAction(provider, formData, callbackUrl) {
    const id = formData.get('email')?.toString();
    const password = formData.get('password')?.toString();

    const res = await axiosInstance.post('/login', {
        employee_id: id,
        password: password,
    });

    const token = res.data?.access_token;
    if (token) {
        localStorage.setItem('jwt', token);
        redirect(callbackUrl ?? '/');
    }
    if (globalErrorHandler) {
        globalErrorHandler('登录失败，请检查工号和密码');
        return null;
    }
}