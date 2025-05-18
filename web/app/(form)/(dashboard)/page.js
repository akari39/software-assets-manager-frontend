'use client';

import { Stack, CircularProgress, Box } from "@mui/material";
import { useEffect, useState } from 'react';
import axiosInstance from '@/app/service/axios';
import DashboardItem from './components/DashboardItem';

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const response = await axiosInstance.get('/dashboard');
        setStatus(response.data);
      } catch (err) {
        console.log('Fetch dashboard stats failed', err);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Stack direction="column">
      <Stack
        direction={{ sm: 'column', md: 'row' }}
        spacing={{ xs: 2, sm: 2, md: 4 }}
        padding="32px"
      >
        <DashboardItem
          number={status?.used_licenses}
          title="正在使用"
          href="/dashboard/software"
          tintColor="green"
        />
        <DashboardItem
          number={status?.approching_expired_licenses}
          title="即将过期"
          href="/dashboard/software"
          tintColor="red"
        />
        <DashboardItem
          number={status?.apllicable_licenses}
          title="可领用"
          href="/dashboard/software"
          tintColor="blue"
        />
      </Stack>
    </Stack>
  );
}