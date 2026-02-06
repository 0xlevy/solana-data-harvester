'use client';

import { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface TokenMetrics {
  total_transfers: number;
  token_transfer_counts: Record<string, number>;
  most_active_token: string;
}

interface TokenActivityProps {
  metrics: TokenMetrics;
}

export default function TokenActivity({ metrics }: TokenActivityProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    const labels = Object.keys(metrics.token_transfer_counts);
    const data = Object.values(metrics.token_transfer_counts);

    const colors = [
      'rgba(153, 69, 255, 0.8)',  // Purple (USDC)
      'rgba(20, 241, 149, 0.8)',   // Green (USDT)
      'rgba(59, 130, 246, 0.8)',   // Blue (SOL)
      'rgba(251, 191, 36, 0.8)',   // Yellow (JUP)
      'rgba(236, 72, 153, 0.8)',   // Pink
    ];

    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Transfers',
          data: data,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: colors.slice(0, labels.length).map(c => c.replace('0.8', '1')),
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
            },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [metrics]);

  return (
    <div className="bg-solana-dark/50 rounded-xl border border-white/10 p-6 card-glow">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Token Activity</h2>
        <span className="px-3 py-1 bg-solana-purple/20 text-solana-purple rounded-full text-sm">
          {metrics.total_transfers} transfers
        </span>
      </div>

      <div className="bg-white/5 rounded-lg p-3 mb-4">
        <p className="text-gray-400 text-sm">Most Active Token</p>
        <p className="text-lg font-bold text-white flex items-center gap-2 mt-1">
          <span className="w-2 h-2 bg-solana-purple rounded-full"></span>
          {metrics.most_active_token}
        </p>
      </div>

      <div className="h-48">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
}
