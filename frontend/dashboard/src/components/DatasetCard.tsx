'use client';

import { useState } from 'react';

interface DatasetCardProps {
  id: string;
  title: string;
  description: string;
  price: number;
  dataPoints: number;
}

export default function DatasetCard({ id, title, description, price, dataPoints }: DatasetCardProps) {
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [isPurchased, setIsPurchased] = useState(false);

  const handlePurchase = async () => {
    setIsPurchasing(true);
    
    // Simulate purchase process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsPurchasing(false);
    setIsPurchased(true);
  };

  const handleDownload = () => {
    // Simulate download
    alert(`Downloading dataset: ${id}`);
  };

  return (
    <div className="bg-solana-dark/50 rounded-xl border border-white/10 p-6 card-glow flex flex-col">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <span className="px-2 py-1 bg-solana-purple/20 text-solana-purple rounded text-sm font-medium">
          ${price.toFixed(2)}
        </span>
      </div>

      <p className="text-gray-400 text-sm mb-4 flex-1">{description}</p>

      <div className="flex items-center gap-4 mb-4 text-sm">
        <div className="flex items-center gap-1 text-gray-400">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>{dataPoints.toLocaleString()} data points</span>
        </div>
        <div className="flex items-center gap-1 text-gray-400">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Updated 5m ago</span>
        </div>
      </div>

      {isPurchased ? (
        <button
          onClick={handleDownload}
          className="w-full py-2 px-4 bg-solana-green/20 text-solana-green border border-solana-green/30 rounded-lg font-medium hover:bg-solana-green/30 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download Dataset
        </button>
      ) : (
        <button
          onClick={handlePurchase}
          disabled={isPurchasing}
          className="w-full py-2 px-4 bg-solana-purple text-white rounded-lg font-medium hover:bg-solana-purple/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isPurchasing ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Buy with USDC
            </>
          )}
        </button>
      )}

      <p className="text-center text-xs text-gray-500 mt-2">
        Powered by AgentWallet
      </p>
    </div>
  );
}
