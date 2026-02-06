'use client';

import { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface TransactionMetrics {
  total_transactions: number;
  success_rate_percent: number;
  sample_tps: number;
  failed_transactions: number;
}

interface TransactionChartProps {
  metrics: TransactionMetrics;
}

export default function TransactionChart({ metrics }: TransactionChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    const successfulTx = metrics.total_transactions - metrics.failed_transactions;

    chartInstance.current = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Successful', 'Failed'],
        datasets: [{
          data: [successfulTx, metrics.failed_transactions],
          backgroundColor: [
            'rgba(20, 241, 149, 0.8)',
            'rgba(239, 68, 68, 0.8)',
          ],
          borderColor: [
            'rgba(20, 241, 149, 1)',
            'rgba(239, 68, 68, 1)',
          ],
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: 'rgba(255, 255, 255, 0.7)',
              padding: 20,
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
      <h2 className="text-xl font-semibold text-white mb-4">Transaction Analysis</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-sm">Total Transactions</p>
          <p className="text-xl font-bold text-white">{metrics.total_transactions.toLocaleString()}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-sm">Success Rate</p>
          <p className="text-xl font-bold text-solana-green">{metrics.success_rate_percent}%</p>
        </div>
      </div>

      <div className="h-64 relative">
        <canvas ref={chartRef}></canvas>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{metrics.sample_tps}</p>
            <p className="text-sm text-gray-400">TPS</p>
          </div>
        </div>
      </div>
    </div>
  );
}
