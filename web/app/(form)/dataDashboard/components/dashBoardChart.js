'use client';

import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto'; // 引入 Chart.js

export default function DashboardChart({ data }) {
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null); // 保存图表实例

    useEffect(() => {
        if (!data || !chartRef.current) return;

        const ctx = chartRef.current.getContext('2d');

        // 销毁已有图表实例（防止重复渲染）
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }

        chartInstanceRef.current = new Chart(ctx, {
            type: 'bar', // 可改为 'line', 'pie' 等
            data: {
                labels: data.categories || [],
                datasets: [{
                    label: '数据统计',
                    data: data.values || [],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        enabled: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        return () => {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
        };
    }, [data]);

    return <canvas ref={chartRef} />;
}