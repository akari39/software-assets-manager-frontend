'use client';

import { NextAppProvider } from '@toolpad/core/nextjs';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppsIcon from '@mui/icons-material/Apps';
import theme from './styles/theme';
import { ErrorProvider } from './context/ErrorProvider';
import GlobalSnackbar from './components/GlobalSnackbar';
import { Suspense } from 'react';
import { LinearProgress } from '@mui/material';

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
  return (
    <html lang="zh-cn">
      <body>
        <ErrorProvider>
          <GlobalSnackbar />
          <AppRouterCacheProvider>
            <Suspense fallback={<LinearProgress />}>
              <NextAppProvider
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
