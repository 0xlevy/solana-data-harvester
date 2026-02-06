"""
Solana Data Collector Module
Collects on-chain data from Solana using Helius API and Solana RPC.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class SolanaDataCollector:
    """
    Autonomous Solana data collector using Helius API.
    Fetches transactions, token transfers, NFT activity, and DEX trades.
    """
    
    def __init__(self):
        self.helius_api_key = os.getenv("HELIUS_API_KEY", "")
        self.helius_base_url = f"https://api.helius.xyz/v0"
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.collected_data: Dict[str, Any] = {}
        
    async def _make_helius_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make async request to Helius API."""
        url = f"{self.helius_base_url}/{endpoint}?api-key={self.helius_api_key}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Helius API error: {response.status}")
                        return {}
            except Exception as e:
                print(f"Request error: {e}")
                return {}
    
    async def _make_rpc_request(self, method: str, params: List = None) -> Dict:
        """Make async RPC request to Solana."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result", {})
                    return {}
            except Exception as e:
                print(f"RPC error: {e}")
                return {}
    
    async def fetch_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """
        Fetch recent transactions from Solana network.
        Uses Helius enhanced transactions API for richer data.
        """
        print(f"[Collector] Fetching {limit} recent transactions...")
        
        # Get recent signatures from RPC
        signatures_result = await self._make_rpc_request(
            "getSignaturesForAddress",
            [
                "So11111111111111111111111111111111111111112",  # Wrapped SOL
                {"limit": limit}
            ]
        )
        
        transactions = []
        if isinstance(signatures_result, list):
            for sig_info in signatures_result[:limit]:
                tx_data = {
                    "signature": sig_info.get("signature"),
                    "slot": sig_info.get("slot"),
                    "blockTime": sig_info.get("blockTime"),
                    "err": sig_info.get("err"),
                    "memo": sig_info.get("memo"),
                    "confirmationStatus": sig_info.get("confirmationStatus")
                }
                transactions.append(tx_data)
        
        self.collected_data["recent_transactions"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(transactions),
            "data": transactions
        }
        
        print(f"[Collector] Collected {len(transactions)} transactions")
        return transactions
    
    async def fetch_token_transfers(self, token_mint: str = None, limit: int = 50) -> List[Dict]:
        """
        Fetch recent token transfers.
        Uses Helius parsed transaction history for token movements.
        """
        print(f"[Collector] Fetching token transfers...")
        
        # Popular token mints to track
        token_mints = [
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "So11111111111111111111111111111111111111112",   # Wrapped SOL
        ]
        
        if token_mint:
            token_mints = [token_mint]
        
        transfers = []
        for mint in token_mints:
            signatures = await self._make_rpc_request(
                "getSignaturesForAddress",
                [mint, {"limit": limit}]
            )
            
            if isinstance(signatures, list):
                for sig in signatures:
                    transfer_data = {
                        "tokenMint": mint,
                        "signature": sig.get("signature"),
                        "slot": sig.get("slot"),
                        "blockTime": sig.get("blockTime"),
                        "type": "transfer"
                    }
                    transfers.append(transfer_data)
        
        self.collected_data["token_transfers"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(transfers),
            "data": transfers
        }
        
        print(f"[Collector] Collected {len(transfers)} token transfers")
        return transfers
    
    async def fetch_nft_activity(self, limit: int = 25) -> List[Dict]:
        """
        Fetch recent NFT marketplace activity.
        Tracks NFT mints, sales, and transfers.
        """
        print(f"[Collector] Fetching NFT activity...")
        
        # Known NFT marketplace programs
        marketplace_programs = [
            "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K",   # Magic Eden v2
            "hausS13jsjafwWwGqZTUQRmWyvyxn9EQpqMwV1PBBmk",  # Haus
        ]
        
        nft_activities = []
        for program in marketplace_programs:
            signatures = await self._make_rpc_request(
                "getSignaturesForAddress",
                [program, {"limit": limit}]
            )
            
            if isinstance(signatures, list):
                for sig in signatures:
                    activity = {
                        "marketplace": program[:8] + "...",
                        "signature": sig.get("signature"),
                        "slot": sig.get("slot"),
                        "blockTime": sig.get("blockTime"),
                        "type": "nft_activity"
                    }
                    nft_activities.append(activity)
        
        self.collected_data["nft_activity"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(nft_activities),
            "data": nft_activities
        }
        
        print(f"[Collector] Collected {len(nft_activities)} NFT activities")
        return nft_activities
    
    async def fetch_dex_trades(self, limit: int = 50) -> List[Dict]:
        """
        Fetch recent DEX trades from major Solana DEXs.
        Tracks swaps on Raydium, Orca, Jupiter, etc.
        """
        print(f"[Collector] Fetching DEX trades...")
        
        # Major DEX program IDs
        dex_programs = [
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium AMM
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",  # Orca Whirlpool
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter v6
        ]
        
        dex_trades = []
        for program in dex_programs:
            signatures = await self._make_rpc_request(
                "getSignaturesForAddress",
                [program, {"limit": limit}]
            )
            
            if isinstance(signatures, list):
                for sig in signatures:
                    trade = {
                        "dex": program[:8] + "...",
                        "signature": sig.get("signature"),
                        "slot": sig.get("slot"),
                        "blockTime": sig.get("blockTime"),
                        "type": "swap"
                    }
                    dex_trades.append(trade)
        
        self.collected_data["dex_trades"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(dex_trades),
            "data": dex_trades
        }
        
        print(f"[Collector] Collected {len(dex_trades)} DEX trades")
        return dex_trades
    
    async def fetch_network_stats(self) -> Dict:
        """
        Fetch current Solana network statistics.
        Includes TPS, slot, epoch info, etc.
        """
        print(f"[Collector] Fetching network stats...")
        
        # Get epoch info
        epoch_info = await self._make_rpc_request("getEpochInfo")
        
        # Get recent performance samples
        perf_samples = await self._make_rpc_request(
            "getRecentPerformanceSamples",
            [5]
        )
        
        # Calculate average TPS
        avg_tps = 0
        if isinstance(perf_samples, list) and len(perf_samples) > 0:
            total_txs = sum(s.get("numTransactions", 0) for s in perf_samples)
            total_slots = sum(s.get("numSlots", 1) for s in perf_samples)
            avg_tps = total_txs / (total_slots * 0.4) if total_slots > 0 else 0  # ~400ms per slot
        
        # Get supply info
        supply_info = await self._make_rpc_request("getSupply")
        
        network_stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "epoch": epoch_info.get("epoch", 0) if isinstance(epoch_info, dict) else 0,
            "slot": epoch_info.get("absoluteSlot", 0) if isinstance(epoch_info, dict) else 0,
            "slotIndex": epoch_info.get("slotIndex", 0) if isinstance(epoch_info, dict) else 0,
            "slotsInEpoch": epoch_info.get("slotsInEpoch", 0) if isinstance(epoch_info, dict) else 0,
            "averageTPS": round(avg_tps, 2),
            "totalSupply": supply_info.get("value", {}).get("total", 0) if isinstance(supply_info, dict) else 0,
            "circulatingSupply": supply_info.get("value", {}).get("circulating", 0) if isinstance(supply_info, dict) else 0
        }
        
        self.collected_data["network_stats"] = network_stats
        
        print(f"[Collector] Network stats collected - Epoch: {network_stats['epoch']}, TPS: {network_stats['averageTPS']}")
        return network_stats
    
    async def collect_all(self) -> Dict[str, Any]:
        """
        Run full collection cycle - gathers all data types.
        This is the main entry point for the agent loop.
        """
        print("\n" + "="*60)
        print(f"[Collector] Starting full data collection cycle...")
        print(f"[Collector] Timestamp: {datetime.utcnow().isoformat()}")
        print("="*60 + "\n")
        
        # Run all collection tasks concurrently
        await asyncio.gather(
            self.fetch_recent_transactions(),
            self.fetch_token_transfers(),
            self.fetch_nft_activity(),
            self.fetch_dex_trades(),
            self.fetch_network_stats()
        )
        
        # Add collection metadata
        self.collected_data["metadata"] = {
            "collection_timestamp": datetime.utcnow().isoformat(),
            "helius_api_configured": bool(self.helius_api_key),
            "rpc_url": self.rpc_url,
            "total_data_points": sum(
                self.collected_data.get(key, {}).get("count", 0)
                for key in ["recent_transactions", "token_transfers", "nft_activity", "dex_trades"]
            )
        }
        
        print("\n" + "="*60)
        print(f"[Collector] Collection complete!")
        print(f"[Collector] Total data points: {self.collected_data['metadata']['total_data_points']}")
        print("="*60 + "\n")
        
        return self.collected_data
    
    def get_collected_data(self) -> Dict[str, Any]:
        """Return the most recently collected data."""
        return self.collected_data
    
    def clear_data(self):
        """Clear collected data for next cycle."""
        self.collected_data = {}


# Standalone test
if __name__ == "__main__":
    async def test_collector():
        collector = SolanaDataCollector()
        data = await collector.collect_all()
        print(json.dumps(data.get("metadata", {}), indent=2))
    
    asyncio.run(test_collector())
