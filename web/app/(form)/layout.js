'use client';

import { DashboardLayout } from "@toolpad/core";
import SAMPageContainer from "../components/SamPageContainer";
import AuthGuard from "../components/AuthGuard";
import { useEffect, useMemo, useState } from "react"
import AppRegistrationIcon from '@mui/icons-material/AppRegistration';
import SsidChartIcon from '@mui/icons-material/SsidChart';
import PersonIcon from '@mui/icons-material/Person';
import axiosInstance from '../service/axiosConfig';
import { redirect } from 'next/navigation';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppsIcon from '@mui/icons-material/Apps';
import { NextAppProvider } from '@toolpad/core/nextjs';
import { signOutAction } from "../auth/actions";
import theme from "../styles/theme";

const NAVIGATION = [
    {
        segment: '',
        title: '仪表盘',
        icon: <DashboardIcon />,
    },
    {
        segment: 'software',
        title: '软件资产',
        icon: <AppsIcon />,
    },
    {
        segment: 'softwareDetail',
        title: '软件信息',
        icon: <AppRegistrationIcon />,
    },
    {
        segment: 'dataDashboard',
        title: '数据看板',
        icon: <SsidChartIcon />,
    },
    {
        segment: 'userManagement',
        title: '用户管理',
        icon: <PersonIcon />,
    }
];

const BRANDING = {
    title: '软件资产管理',
};

export function getTitleByPath(pathname) {
    const rawPathName = pathname.split('/')[1]
    const match = NAVIGATION.find((item) => rawPathName === item.segment);
    return match?.title || '';
}

export default function FormLayout({ children }) {
    const [session, setSession] = useState('');

    useEffect(() => {
        (async () => {
            const employeeId = localStorage.getItem('employee_id');
            console.log('employeeId', employeeId);
            if (employeeId === null || employeeId === undefined) {
                setSession(null);
                return;
            }
            const userRes = await axiosInstance.get(`/users/by_employee_id/${employeeId}`);
            setSession({
                user: {
                    name: userRes.data.employee.name,
                },
            });
        })();
    }, []);

    const authentication = useMemo(() => {
        return {
            signIn: () => {
                redirect('/auth/signin');
            },
            signOut: () => {
                signOutAction();
            },
        };
    }, []);

    return (
        <NextAppProvider
            session={session}
            authentication={session === '' ? null : authentication}
            navigation={NAVIGATION}
            branding={BRANDING}
            theme={theme}>
            <AuthGuard>
                <DashboardLayout>
                    <SAMPageContainer>
                        {children}
                    </SAMPageContainer>
                </DashboardLayout>
            </AuthGuard>
        </NextAppProvider>
    );
}