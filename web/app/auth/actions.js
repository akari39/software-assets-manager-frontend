import axiosInstance, { globalErrorHandler } from '@/app/service/axiosConfig';

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
        console.error(error);
        if (globalErrorHandler) {
            globalErrorHandler('登录失败，请检查工号和密码');
        }
        return false;
    }
}

export function signOutAction() {
    localStorage.removeItem('jwt');
    localStorage.removeItem('employee_id');
}
