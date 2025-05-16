'use client';

import { NextAppProvider } from '@toolpad/core/nextjs';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppsIcon from '@mui/icons-material/Apps';
import theme from './styles/theme';
import { ErrorProvider } from './context/ErrorProvider';
import GlobalSnackbar from './components/GlobalSnackbar';
import { Suspense, useMemo, useState } from 'react';
import { LinearProgress } from '@mui/material';
import AppRegistrationIcon from '@mui/icons-material/AppRegistration';
import SsidChartIcon from '@mui/icons-material/SsidChart';
import PersonIcon from '@mui/icons-material/Person';
import AuthGuard from './components/AuthGuard';

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

export default function RootLayout({ children }) {
  const [session, setSession] = useState({
    user: {
      name: 'Bharat Kashyap',
      email: 'bharatkashyap@outlook.com',
      image: 'https://avatars.githubusercontent.com/u/19550456',
    },
  });

  const authentication = useMemo(() => {
    return {
      signIn: () => {
        setSession({
          user: {
            name: 'Bharat Kashyap',
            email: 'bharatkashyap@outlook.com',
            image: 'https://avatars.githubusercontent.com/u/19550456',
          },
        });
      },
      signOut: () => {
        setSession(null);
      },
    };
  }, []);

  return (
    <html lang="zh-cn">
      <body>
        <ErrorProvider>
          <GlobalSnackbar />
          <AppRouterCacheProvider>
            <Suspense fallback={<LinearProgress />}>
              <NextAppProvider
                session={session}
                authentication={authentication}
                navigation={NAVIGATION}
                branding={BRANDING}
                theme={theme}>
                {children}
              </NextAppProvider>
            </Suspense>
          </AppRouterCacheProvider>
        </ErrorProvider>
      </body>
    </html>
  );
}
