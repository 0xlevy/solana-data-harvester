'use client';

import { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface DexMetrics {
  total_dex_trades: number;
  dex_trade_counts: Record<string, number>;
  dex_share_percent: Record<string, number>;
  dominant_dex: string;
}

interface DexAnalysisProps {
  metrics: DexMetrics;
}

export default function DexAnalysis({ metrics }: DexAnalysisProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    const labels = Object.keys(metrics.dex_share_percent);
    const data = Object.values(metrics.dex_share_percent);

    chartInstance.current = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(153, 69, 255, 0.8)',
            'rgba(20, 241, 149, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(251, 191, 36, 0.8)',
            'rgba(236, 72, 153, 0.8)',
          ],
          borderColor: 'rgba(14, 14, 26, 0.5)',
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: 'rgba(255, 255, 255, 0.7)',
              padding: 15,
              usePointStyle: true,
            },
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                return `${context.label}: ${context.parsed}%`;
              },
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
        <h2 className="text-xl font-semibold text-white">DEX Activity</h2>
        <span className="px-3 py-1 bg-solana-green/20 text-solana-green rounded-full text-sm">
          {metrics.total_dex_trades.toLocaleString()} swaps
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-gray-400 text-xs">Leading DEX</p>
          <p className="text-lg font-bold text-white">{metrics.dominant_dex}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-gray-400 text-xs">Market Share</p>
          <p className="text-lg font-bold text-solana-purple">
            {metrics.dex_share_percent[metrics.dominant_dex]}%
          </p>
        </div>
      </div>

      <div className="h-48">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
}
