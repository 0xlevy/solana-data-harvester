'use client';

interface NetworkMetrics {
  current_epoch: number;
  current_slot: number;
  average_tps: number;
  network_health: string;
  epoch_progress_percent: number;
  total_supply_sol: number;
  circulating_supply_sol: number;
}

interface NetworkStatsProps {
  metrics: NetworkMetrics;
}

export default function NetworkStats({ metrics }: NetworkStatsProps) {
  const healthColor = metrics.network_health === 'healthy' 
    ? 'text-solana-green' 
    : metrics.network_health === 'degraded' 
    ? 'text-yellow-400' 
    : 'text-red-400';

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="bg-solana-dark/50 rounded-xl border border-white/10 p-6 card-glow">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Network Overview</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${healthColor === 'text-solana-green' ? 'bg-solana-green' : 'bg-yellow-400'} status-pulse`}></div>
          <span className={`text-sm font-medium ${healthColor} capitalize`}>
            {metrics.network_health}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* TPS */}
        <div className="bg-white/5 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Average TPS</p>
          <p className="text-2xl font-bold text-white mt-1">
            {formatNumber(metrics.average_tps)}
          </p>
          <p className="text-xs text-gray-500 mt-1">transactions/sec</p>
        </div>

        {/* Current Epoch */}
        <div className="bg-white/5 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Current Epoch</p>
          <p className="text-2xl font-bold text-white mt-1">
            {formatNumber(metrics.current_epoch)}
          </p>
          <div className="mt-2">
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div 
                className="bg-solana-purple h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.epoch_progress_percent}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{metrics.epoch_progress_percent.toFixed(1)}% complete</p>
          </div>
        </div>

        {/* Current Slot */}
        <div className="bg-white/5 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Current Slot</p>
          <p className="text-2xl font-bold text-white mt-1">
            {formatNumber(metrics.current_slot)}
          </p>
          <p className="text-xs text-gray-500 mt-1">block height</p>
        </div>

        {/* Circulating Supply */}
        <div className="bg-white/5 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Circulating Supply</p>
          <p className="text-2xl font-bold text-white mt-1">
            {(metrics.circulating_supply_sol / 1e6).toFixed(1)}M
          </p>
          <p className="text-xs text-gray-500 mt-1">
            of {(metrics.total_supply_sol / 1e6).toFixed(1)}M SOL
          </p>
        </div>
      </div>
    </div>
  );
}
