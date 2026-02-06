"""
Solana Data Analyzer Module
Aggregates and analyzes collected Solana on-chain data for insights.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import pandas as pd
import numpy as np


class SolanaDataAnalyzer:
    """
    Analyzes collected Solana data to produce meaningful metrics and insights.
    Generates aggregated reports for tokens, DEX activity, NFTs, and network health.
    """
    
    def __init__(self):
        self.analysis_results: Dict[str, Any] = {}
        self.raw_data: Dict[str, Any] = {}
    
    def load_data(self, collected_data: Dict[str, Any]):
        """Load collected data for analysis."""
        self.raw_data = collected_data
        print(f"[Analyzer] Loaded data with {collected_data.get('metadata', {}).get('total_data_points', 0)} data points")
    
    def analyze_transactions(self) -> Dict[str, Any]:
        """
        Analyze recent transaction patterns.
        Calculates success rates, timing patterns, and volume metrics.
        """
        print("[Analyzer] Analyzing transactions...")
        
        tx_data = self.raw_data.get("recent_transactions", {}).get("data", [])
        
        if not tx_data:
            return {"error": "No transaction data available"}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(tx_data)
        
        # Calculate metrics
        total_txs = len(df)
        successful_txs = len(df[df["err"].isna()]) if "err" in df.columns else total_txs
        failed_txs = total_txs - successful_txs
        success_rate = (successful_txs / total_txs * 100) if total_txs > 0 else 0
        
        # Time-based analysis
        if "blockTime" in df.columns and df["blockTime"].notna().any():
            df["datetime"] = pd.to_datetime(df["blockTime"], unit="s", errors="coerce")
            
            # Get time range
            min_time = df["datetime"].min()
            max_time = df["datetime"].max()
            time_span_seconds = (max_time - min_time).total_seconds() if pd.notna(min_time) and pd.notna(max_time) else 0
            
            # Calculate TPS over sample period
            tps = total_txs / time_span_seconds if time_span_seconds > 0 else 0
        else:
            time_span_seconds = 0
            tps = 0
        
        # Slot analysis
        if "slot" in df.columns:
            slot_range = df["slot"].max() - df["slot"].min()
            avg_tx_per_slot = total_txs / slot_range if slot_range > 0 else 0
        else:
            slot_range = 0
            avg_tx_per_slot = 0
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_transactions": total_txs,
            "successful_transactions": successful_txs,
            "failed_transactions": failed_txs,
            "success_rate_percent": round(success_rate, 2),
            "sample_tps": round(tps, 2),
            "slot_range": slot_range,
            "avg_tx_per_slot": round(avg_tx_per_slot, 2),
            "sample_period_seconds": round(time_span_seconds, 2)
        }
        
        self.analysis_results["transaction_analysis"] = analysis
        print(f"[Analyzer] Transaction analysis complete - Success rate: {success_rate:.2f}%")
        return analysis
    
    def analyze_token_activity(self) -> Dict[str, Any]:
        """
        Analyze token transfer patterns.
        Identifies popular tokens, volume trends, and transfer frequency.
        """
        print("[Analyzer] Analyzing token activity...")
        
        transfer_data = self.raw_data.get("token_transfers", {}).get("data", [])
        
        if not transfer_data:
            return {"error": "No token transfer data available"}
        
        df = pd.DataFrame(transfer_data)
        
        # Token popularity
        token_counts = df["tokenMint"].value_counts().to_dict() if "tokenMint" in df.columns else {}
        
        # Token labels mapping
        token_labels = {
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
            "So11111111111111111111111111111111111111112": "Wrapped SOL",
        }
        
        # Create labeled counts
        labeled_counts = {}
        for mint, count in token_counts.items():
            label = token_labels.get(mint, mint[:8] + "...")
            labeled_counts[label] = count
        
        # Time analysis
        if "blockTime" in df.columns and df["blockTime"].notna().any():
            df["datetime"] = pd.to_datetime(df["blockTime"], unit="s", errors="coerce")
            df["hour"] = df["datetime"].dt.hour
            hourly_activity = df["hour"].value_counts().sort_index().to_dict()
        else:
            hourly_activity = {}
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_transfers": len(df),
            "unique_tokens": len(token_counts),
            "token_transfer_counts": labeled_counts,
            "most_active_token": max(labeled_counts, key=labeled_counts.get) if labeled_counts else None,
            "hourly_activity_distribution": hourly_activity
        }
        
        self.analysis_results["token_analysis"] = analysis
        print(f"[Analyzer] Token analysis complete - {len(df)} transfers across {len(token_counts)} tokens")
        return analysis
    
    def analyze_nft_market(self) -> Dict[str, Any]:
        """
        Analyze NFT marketplace activity.
        Tracks marketplace dominance and activity patterns.
        """
        print("[Analyzer] Analyzing NFT marketplace activity...")
        
        nft_data = self.raw_data.get("nft_activity", {}).get("data", [])
        
        if not nft_data:
            return {"error": "No NFT activity data available"}
        
        df = pd.DataFrame(nft_data)
        
        # Marketplace activity
        marketplace_counts = df["marketplace"].value_counts().to_dict() if "marketplace" in df.columns else {}
        
        # Map short addresses to names
        marketplace_names = {
            "M2mx93ek": "Magic Eden",
            "hausS13j": "Haus",
        }
        
        labeled_marketplaces = {}
        for addr, count in marketplace_counts.items():
            name = marketplace_names.get(addr, addr)
            labeled_marketplaces[name] = count
        
        # Calculate market share
        total_activity = len(df)
        market_share = {
            name: round(count / total_activity * 100, 2) 
            for name, count in labeled_marketplaces.items()
        } if total_activity > 0 else {}
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_nft_activities": total_activity,
            "marketplace_activity": labeled_marketplaces,
            "marketplace_share_percent": market_share,
            "dominant_marketplace": max(labeled_marketplaces, key=labeled_marketplaces.get) if labeled_marketplaces else None
        }
        
        self.analysis_results["nft_analysis"] = analysis
        print(f"[Analyzer] NFT analysis complete - {total_activity} activities tracked")
        return analysis
    
    def analyze_dex_activity(self) -> Dict[str, Any]:
        """
        Analyze DEX trading activity.
        Tracks swap volume and DEX usage patterns.
        """
        print("[Analyzer] Analyzing DEX activity...")
        
        dex_data = self.raw_data.get("dex_trades", {}).get("data", [])
        
        if not dex_data:
            return {"error": "No DEX trade data available"}
        
        df = pd.DataFrame(dex_data)
        
        # DEX activity counts
        dex_counts = df["dex"].value_counts().to_dict() if "dex" in df.columns else {}
        
        # Map to DEX names
        dex_names = {
            "675kPX9M": "Raydium",
            "whirLbMi": "Orca Whirlpool",
            "JUP6LkbZ": "Jupiter",
        }
        
        labeled_dex = {}
        for addr, count in dex_counts.items():
            name = dex_names.get(addr, addr)
            labeled_dex[name] = count
        
        # Calculate shares
        total_trades = len(df)
        dex_share = {
            name: round(count / total_trades * 100, 2)
            for name, count in labeled_dex.items()
        } if total_trades > 0 else {}
        
        # Time-based trading patterns
        if "blockTime" in df.columns and df["blockTime"].notna().any():
            df["datetime"] = pd.to_datetime(df["blockTime"], unit="s", errors="coerce")
            df["hour"] = df["datetime"].dt.hour
            
            # Peak trading hours
            hourly_trades = df["hour"].value_counts().sort_index()
            peak_hour = hourly_trades.idxmax() if len(hourly_trades) > 0 else None
        else:
            peak_hour = None
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_dex_trades": total_trades,
            "dex_trade_counts": labeled_dex,
            "dex_share_percent": dex_share,
            "dominant_dex": max(labeled_dex, key=labeled_dex.get) if labeled_dex else None,
            "peak_trading_hour_utc": int(peak_hour) if peak_hour is not None else None
        }
        
        self.analysis_results["dex_analysis"] = analysis
        print(f"[Analyzer] DEX analysis complete - {total_trades} trades across {len(labeled_dex)} DEXs")
        return analysis
    
    def analyze_network_health(self) -> Dict[str, Any]:
        """
        Analyze network health metrics.
        Evaluates TPS, epoch progress, and overall network status.
        """
        print("[Analyzer] Analyzing network health...")
        
        network_data = self.raw_data.get("network_stats", {})
        
        if not network_data:
            return {"error": "No network stats available"}
        
        # Calculate epoch progress
        slot_index = network_data.get("slotIndex", 0)
        slots_in_epoch = network_data.get("slotsInEpoch", 1)
        epoch_progress = (slot_index / slots_in_epoch * 100) if slots_in_epoch > 0 else 0
        
        # Estimate time until epoch end
        slots_remaining = slots_in_epoch - slot_index
        estimated_seconds_remaining = slots_remaining * 0.4  # ~400ms per slot
        estimated_hours_remaining = estimated_seconds_remaining / 3600
        
        # TPS health assessment
        avg_tps = network_data.get("averageTPS", 0)
        if avg_tps >= 3000:
            tps_status = "excellent"
        elif avg_tps >= 1500:
            tps_status = "good"
        elif avg_tps >= 500:
            tps_status = "moderate"
        else:
            tps_status = "low"
        
        # Calculate supply metrics
        total_supply = network_data.get("totalSupply", 0)
        circulating = network_data.get("circulatingSupply", 0)
        staked_estimate = total_supply - circulating if total_supply > 0 else 0
        staked_percent = (staked_estimate / total_supply * 100) if total_supply > 0 else 0
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_epoch": network_data.get("epoch", 0),
            "current_slot": network_data.get("slot", 0),
            "epoch_progress_percent": round(epoch_progress, 2),
            "estimated_hours_until_epoch_end": round(estimated_hours_remaining, 2),
            "average_tps": avg_tps,
            "tps_status": tps_status,
            "total_supply_sol": round(total_supply / 1e9, 2) if total_supply > 0 else 0,
            "circulating_supply_sol": round(circulating / 1e9, 2) if circulating > 0 else 0,
            "estimated_staked_percent": round(staked_percent, 2),
            "network_health": "healthy" if tps_status in ["excellent", "good"] else "degraded"
        }
        
        self.analysis_results["network_health"] = analysis
        print(f"[Analyzer] Network analysis complete - Status: {analysis['network_health']}")
        return analysis
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of all analyses.
        This is the main output for the publisher module.
        """
        print("\n[Analyzer] Generating comprehensive summary...")
        
        summary = {
            "generated_at": datetime.utcnow().isoformat(),
            "data_collection_time": self.raw_data.get("metadata", {}).get("collection_timestamp"),
            "total_data_points_analyzed": self.raw_data.get("metadata", {}).get("total_data_points", 0),
            "analyses": {
                "transactions": self.analysis_results.get("transaction_analysis", {}),
                "tokens": self.analysis_results.get("token_analysis", {}),
                "nft": self.analysis_results.get("nft_analysis", {}),
                "dex": self.analysis_results.get("dex_analysis", {}),
                "network": self.analysis_results.get("network_health", {})
            },
            "highlights": self._generate_highlights()
        }
        
        self.analysis_results["summary"] = summary
        return summary
    
    def _generate_highlights(self) -> List[str]:
        """Generate human-readable highlights from the analysis."""
        highlights = []
        
        # Transaction highlights
        tx_analysis = self.analysis_results.get("transaction_analysis", {})
        if tx_analysis and "success_rate_percent" in tx_analysis:
            highlights.append(f"Transaction success rate: {tx_analysis['success_rate_percent']}%")
        
        # Token highlights
        token_analysis = self.analysis_results.get("token_analysis", {})
        if token_analysis and "most_active_token" in token_analysis:
            highlights.append(f"Most active token: {token_analysis['most_active_token']}")
        
        # DEX highlights
        dex_analysis = self.analysis_results.get("dex_analysis", {})
        if dex_analysis and "dominant_dex" in dex_analysis:
            highlights.append(f"Leading DEX: {dex_analysis['dominant_dex']}")
        
        # NFT highlights
        nft_analysis = self.analysis_results.get("nft_analysis", {})
        if nft_analysis and "dominant_marketplace" in nft_analysis:
            highlights.append(f"Top NFT marketplace: {nft_analysis['dominant_marketplace']}")
        
        # Network highlights
        network_analysis = self.analysis_results.get("network_health", {})
        if network_analysis:
            highlights.append(f"Network status: {network_analysis.get('network_health', 'unknown')}")
            highlights.append(f"Average TPS: {network_analysis.get('average_tps', 0)}")
        
        return highlights
    
    def analyze_all(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete analysis pipeline on collected data.
        Main entry point for the agent loop.
        """
        print("\n" + "="*60)
        print("[Analyzer] Starting full analysis cycle...")
        print("="*60 + "\n")
        
        # Load the data
        self.load_data(collected_data)
        
        # Run all analyses
        self.analyze_transactions()
        self.analyze_token_activity()
        self.analyze_nft_market()
        self.analyze_dex_activity()
        self.analyze_network_health()
        
        # Generate summary
        summary = self.generate_summary()
        
        print("\n" + "="*60)
        print("[Analyzer] Analysis complete!")
        print(f"[Analyzer] Generated {len(summary['highlights'])} key insights")
        print("="*60 + "\n")
        
        return summary
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Return all analysis results."""
        return self.analysis_results
    
    def clear_results(self):
        """Clear analysis results for next cycle."""
        self.analysis_results = {}
        self.raw_data = {}


# Standalone test
if __name__ == "__main__":
    # Test with mock data
    mock_data = {
        "metadata": {"total_data_points": 100, "collection_timestamp": datetime.utcnow().isoformat()},
        "recent_transactions": {
            "data": [{"signature": "test", "slot": 123, "blockTime": 1700000000, "err": None} for _ in range(10)]
        },
        "token_transfers": {
            "data": [{"tokenMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "blockTime": 1700000000} for _ in range(10)]
        },
        "nft_activity": {
            "data": [{"marketplace": "M2mx93ek", "blockTime": 1700000000} for _ in range(5)]
        },
        "dex_trades": {
            "data": [{"dex": "675kPX9M", "blockTime": 1700000000} for _ in range(15)]
        },
        "network_stats": {
            "epoch": 500,
            "slot": 200000000,
            "slotIndex": 100000,
            "slotsInEpoch": 432000,
            "averageTPS": 2500,
            "totalSupply": 500000000000000000,
            "circulatingSupply": 400000000000000000
        }
    }
    
    analyzer = SolanaDataAnalyzer()
    results = analyzer.analyze_all(mock_data)
    print("\nHighlights:")
    for h in results["highlights"]:
        print(f"  • {h}")
