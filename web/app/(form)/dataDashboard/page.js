'use client';

import React, { useEffect, useState } from 'react';
import axiosInstance from '@/app/service/axiosConfig';
import DashboardChart from './components/DashboardChart';

export default function DataDashboard() {
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await axiosInstance.get('/api/data-dashboard'); // 替换为实际API路径
                setChartData(response.data);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            }
        }

        fetchData();
    }, []);

    return (
        <div>
            <h1>数据看板</h1>
            {chartData ? (
                <DashboardChart data={chartData} />
            ) : (
                <p>加载中...</p>
            )}
        </div>
    );
}