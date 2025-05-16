'use client';

import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { ErrorProvider } from './context/ErrorProvider';
import GlobalSnackbar from './components/GlobalSnackbar';
import { Suspense } from 'react';
import { LinearProgress } from '@mui/material';
import { NextAppProvider } from '@toolpad/core/nextjs';
import theme from './styles/theme';

export default function RootLayout({ children }) {

  return (
    <html lang="zh-cn">
      <body>
        <ErrorProvider>
          <GlobalSnackbar />
          <AppRouterCacheProvider>
            <Suspense fallback={<LinearProgress />}>
              <NextAppProvider
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
