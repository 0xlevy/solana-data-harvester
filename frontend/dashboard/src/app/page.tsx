'use client';

import { useState, useEffect } from 'react';
import NetworkStats from '@/components/NetworkStats';
import TransactionChart from '@/components/TransactionChart';
import TokenActivity from '@/components/TokenActivity';
import DexAnalysis from '@/components/DexAnalysis';
import NFTMarketplace from '@/components/NFTMarketplace';
import Highlights from '@/components/Highlights';
import DatasetCard from '@/components/DatasetCard';

// Types for our metrics data
interface NetworkMetrics {
  current_epoch: number;
  current_slot: number;
  average_tps: number;
  network_health: string;
  epoch_progress_percent: number;
  total_supply_sol: number;
  circulating_supply_sol: number;
}

interface TransactionMetrics {
  total_transactions: number;
  success_rate_percent: number;
  sample_tps: number;
  failed_transactions: number;
}

interface TokenMetrics {
  total_transfers: number;
  token_transfer_counts: Record<string, number>;
  most_active_token: string;
}

interface DexMetrics {
  total_dex_trades: number;
  dex_trade_counts: Record<string, number>;
  dex_share_percent: Record<string, number>;
  dominant_dex: string;
}

interface NFTMetrics {
  total_nft_activities: number;
  marketplace_activity: Record<string, number>;
  marketplace_share_percent: Record<string, number>;
}

interface DashboardData {
  timestamp: string;
  metrics: {
    network: NetworkMetrics;
    transactions: TransactionMetrics;
    tokens: TokenMetrics;
    dex: DexMetrics;
    nft: NFTMetrics;
  };
  highlights: string[];
}

// Mock data for demo
const mockData: DashboardData = {
  timestamp: new Date().toISOString(),
  metrics: {
    network: {
      current_epoch: 523,
      current_slot: 243567890,
      average_tps: 2847,
      network_health: 'healthy',
      epoch_progress_percent: 67.3,
      total_supply_sol: 571234567,
      circulating_supply_sol: 432567890,
    },
    transactions: {
      total_transactions: 1250,
      success_rate_percent: 98.7,
      sample_tps: 2847,
      failed_transactions: 16,
    },
    tokens: {
      total_transfers: 856,
      token_transfer_counts: {
        'USDC': 412,
        'USDT': 234,
        'Wrapped SOL': 156,
        'JUP': 54,
      },
      most_active_token: 'USDC',
    },
    dex: {
      total_dex_trades: 2340,
      dex_trade_counts: {
        'Jupiter': 987,
        'Raydium': 756,
        'Orca Whirlpool': 432,
        'Phoenix': 165,
      },
      dex_share_percent: {
        'Jupiter': 42.2,
        'Raydium': 32.3,
        'Orca Whirlpool': 18.5,
        'Phoenix': 7.0,
      },
      dominant_dex: 'Jupiter',
    },
    nft: {
      total_nft_activities: 543,
      marketplace_activity: {
        'Magic Eden': 387,
        'Tensor': 112,
        'Haus': 44,
      },
      marketplace_share_percent: {
        'Magic Eden': 71.3,
        'Tensor': 20.6,
        'Haus': 8.1,
      },
    },
  },
  highlights: [
    'Transaction success rate: 98.7%',
    'Most active token: USDC with 412 transfers',
    'Leading DEX: Jupiter with 42.2% market share',
    'Top NFT marketplace: Magic Eden',
    'Network status: healthy',
    'Average TPS: 2,847 transactions/second',
  ],
};

export default function Home() {
  const [data, setData] = useState<DashboardData>(mockData);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isLive, setIsLive] = useState<boolean>(true);

  // Simulate live updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      // Simulate data fluctuation
      setData(prev => ({
        ...prev,
        timestamp: new Date().toISOString(),
        metrics: {
          ...prev.metrics,
          network: {
            ...prev.metrics.network,
            current_slot: prev.metrics.network.current_slot + Math.floor(Math.random() * 10),
            average_tps: prev.metrics.network.average_tps + Math.floor(Math.random() * 200) - 100,
          },
          transactions: {
            ...prev.metrics.transactions,
            total_transactions: prev.metrics.transactions.total_transactions + Math.floor(Math.random() * 50),
          },
        },
      }));
      setLastUpdate(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, [isLive]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">
            Real-time Solana blockchain metrics and analytics
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              isLive
                ? 'bg-solana-green/20 text-solana-green border border-solana-green/30'
                : 'bg-gray-700/50 text-gray-400 border border-gray-600'
            }`}
          >
            {isLive ? '● Live' : '○ Paused'}
          </button>
          <span className="text-sm text-gray-500">
            Last update: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Highlights Banner */}
      <Highlights highlights={data.highlights} />

      {/* Network Stats */}
      <div className="mt-8">
        <NetworkStats metrics={data.metrics.network} />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <TransactionChart metrics={data.metrics.transactions} />
        <TokenActivity metrics={data.metrics.tokens} />
      </div>

      {/* DEX and NFT Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <DexAnalysis metrics={data.metrics.dex} />
        <NFTMarketplace metrics={data.metrics.nft} />
      </div>

      {/* Dataset Purchase Section */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-white mb-6">Available Datasets</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DatasetCard
            id="dataset_20260206_120000"
            title="Full Metrics Bundle"
            description="Complete on-chain analytics including transactions, tokens, DEX trades, and NFT activity."
            price={5.0}
            dataPoints={data.metrics.transactions.total_transactions}
          />
          <DatasetCard
            id="dataset_20260206_120000_dex"
            title="DEX Trading Data"
            description="Detailed DEX swap analysis across Jupiter, Raydium, Orca, and more."
            price={2.0}
            dataPoints={data.metrics.dex.total_dex_trades}
          />
          <DatasetCard
            id="dataset_20260206_120000_nft"
            title="NFT Market Insights"
            description="NFT marketplace activity and trends from Magic Eden, Tensor, and others."
            price={1.5}
            dataPoints={data.metrics.nft.total_nft_activities}
          />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-16 pb-8 text-center text-gray-500 text-sm">
        <p>Autonomous Solana Data Harvester • Colosseum Agent Hackathon 2026</p>
        <p className="mt-1">Powered by Helius API & AgentWallet</p>
      </footer>
    </div>
  );
}
