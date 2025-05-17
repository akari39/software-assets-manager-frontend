'use client';

import { Stack, CircularProgress, Box } from "@mui/material";
import { useEffect, useState } from 'react';
import axiosInstance from '@/app/service/axiosConfig';
import DashboardItem from './components/DashboardItem';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await axiosInstance.get('/dashboard');
        setStats(response.data);
      } catch (err) {
        console.error('Fetch dashboard stats failed', err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
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
          number={stats.used_licenses}
          title="正在使用"
          href="/dashboard/software"
          tintColor="green"
        />
        <DashboardItem
          number={stats.approching_expired_licenses}
          title="即将过期"
          href="/dashboard/software"
          tintColor="red"
        />
        <DashboardItem
          number={stats.apllicable_licenses}
          title="可领用"
          href="/dashboard/software"
          tintColor="blue"
        />
      </Stack>
    </Stack>
  );
}