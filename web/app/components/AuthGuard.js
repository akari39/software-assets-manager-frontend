'use client';

import { redirect, useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AuthGuard({ children }) {
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('jwt');
        if (!token) {
            redirect('/auth/signin');
        }
    }, [router]);

    return <>{children}</>;
}