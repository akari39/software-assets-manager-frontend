import axiosInstance from '@/app/service/axios';
import { globalSnackbarHandler } from '../components/GlobalSnackbar';

export async function signInAction(formData) {
    const id = formData.get('email')?.toString();
    const password = formData.get('password')?.toString();

    try {
        const res = await axiosInstance.post('/login', { employee_id: id, password });
        const token = res.data?.access_token;
        if (!token) throw new Error('No token returned');

        localStorage.setItem('jwt', token);
        localStorage.setItem('employee_id', id);
        return true;
    } catch (error) {
        globalSnackbarHandler({
            tip: error.response?.data?.detail || '发生了一个错误',
            type: 'error',
        });
        return false;
    }
}

export function signOutAction() {
    localStorage.removeItem('jwt');
    localStorage.removeItem('employee_id');
}
