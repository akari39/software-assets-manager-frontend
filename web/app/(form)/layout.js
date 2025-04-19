'use client';

import { NextAppProvider } from '@toolpad/core/nextjs';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { DashboardLayout } from '@toolpad/core/DashboardLayout';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppsIcon from '@mui/icons-material/Apps';
import theme from '../styles/theme';
import SAMPageContainer from '../components/SamPageContainer';

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
        <AppRouterCacheProvider>
          <NextAppProvider
            navigation={NAVIGATION}
            branding={BRANDING}
            theme={theme}>
            <DashboardLayout>
              <SAMPageContainer>
                {children}
              </SAMPageContainer>
            </DashboardLayout>
          </NextAppProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
