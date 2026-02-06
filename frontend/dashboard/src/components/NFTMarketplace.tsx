'use client';

interface NFTMetrics {
  total_nft_activities: number;
  marketplace_activity: Record<string, number>;
  marketplace_share_percent: Record<string, number>;
}

interface NFTMarketplaceProps {
  metrics: NFTMetrics;
}

export default function NFTMarketplace({ metrics }: NFTMarketplaceProps) {
  const sortedMarketplaces = Object.entries(metrics.marketplace_share_percent)
    .sort(([, a], [, b]) => b - a);

  const colors = [
    'bg-solana-purple',
    'bg-solana-green',
    'bg-blue-500',
    'bg-yellow-500',
  ];

  return (
    <div className="bg-solana-dark/50 rounded-xl border border-white/10 p-6 card-glow">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">NFT Marketplace Activity</h2>
        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
          {metrics.total_nft_activities} activities
        </span>
      </div>

      <div className="space-y-4">
        {sortedMarketplaces.map(([name, share], index) => (
          <div key={name} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${colors[index] || 'bg-gray-500'}`}></div>
                <span className="text-white font-medium">{name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-gray-400 text-sm">
                  {metrics.marketplace_activity[name]} trades
                </span>
                <span className="text-white font-medium">{share}%</span>
              </div>
            </div>
            <div className="w-full bg-gray-700/50 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${colors[index] || 'bg-gray-500'}`}
                style={{ width: `${share}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Top Marketplace</span>
          <span className="text-white font-medium flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${colors[0]}`}></span>
            {sortedMarketplaces[0]?.[0] || 'N/A'}
          </span>
        </div>
      </div>
    </div>
  );
}
