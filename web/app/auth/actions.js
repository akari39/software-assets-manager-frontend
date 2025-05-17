'use client';
import axiosInstance, { globalErrorHandler } from '@/app/service/axiosConfig';
import { useRouter } from 'next/navigation';

export async function signInAction(provider, formData, callbackUrl) {
    const id = formData.get('email')?.toString();
    const password = formData.get('password')?.toString();
    const router = useRouter();

    try {
        const res = await axiosInstance.post('/login', { employee_id: id, password });
        const token = res.data?.access_token;
        if (!token) throw new Error('No token returned');

        if (typeof window !== 'undefined') {
            localStorage.setItem('jwt', token);
            localStorage.setItem('employee_id', id);
        }

        router.push(callbackUrl ?? '/');
    } catch (error) {
        console.error(error);
        if (globalErrorHandler) {
            globalErrorHandler('登录失败，请检查工号和密码');
            return null;
        }
    }
}

export function signOutAction() {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('jwt');
        localStorage.removeItem('employee_id');  // fixed key
    }
    // for client-side, router.replace('/') or window.location:
    if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin';
    }
}
