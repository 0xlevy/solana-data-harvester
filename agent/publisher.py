"""
Solana Data Publisher Module
Publishes analyzed data as CSV files, JSON datasets, and to the dashboard API.
Handles dataset monetization via USDC payments through AgentWallet.
"""

import os
import json
import csv
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class DatasetPublisher:
    """
    Publishes analyzed Solana data to various outputs:
    - CSV files for download/sale
    - JSON datasets for API consumption
    - Dashboard API for real-time visualization
    - On-chain PDAs for secure access control
    """
    
    def __init__(self):
        self.output_dir = Path(os.getenv("DATA_OUTPUT_DIR", "./data"))
        self.dashboard_api = os.getenv("DASHBOARD_API_URL", "http://localhost:3000/api")
        self.agent_wallet_key = os.getenv("AGENT_WALLET_KEY", "")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track published datasets
        self.published_datasets: List[Dict] = []
        
    def _generate_dataset_id(self) -> str:
        """Generate unique dataset ID based on timestamp."""
        return f"dataset_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def publish_to_csv(self, analysis_results: Dict[str, Any], dataset_id: str = None) -> Dict[str, str]:
        """
        Export analyzed data to CSV files.
        Creates separate files for each analysis type.
        """
        print("[Publisher] Exporting data to CSV files...")
        
        if not dataset_id:
            dataset_id = self._generate_dataset_id()
        
        csv_files = {}
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create dataset directory
        dataset_dir = self.output_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        analyses = analysis_results.get("analyses", {})
        
        # Export transaction analysis
        if "transactions" in analyses and analyses["transactions"]:
            tx_file = dataset_dir / f"transactions_{timestamp}.csv"
            tx_data = analyses["transactions"]
            with open(tx_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for key, value in tx_data.items():
                    writer.writerow([key, value])
            csv_files["transactions"] = str(tx_file)
            print(f"[Publisher] Created: {tx_file}")
        
        # Export token analysis
        if "tokens" in analyses and analyses["tokens"]:
            token_file = dataset_dir / f"tokens_{timestamp}.csv"
            token_data = analyses["tokens"]
            with open(token_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Token", "Transfer Count"])
                token_counts = token_data.get("token_transfer_counts", {})
                for token, count in token_counts.items():
                    writer.writerow([token, count])
            csv_files["tokens"] = str(token_file)
            print(f"[Publisher] Created: {token_file}")
        
        # Export DEX analysis
        if "dex" in analyses and analyses["dex"]:
            dex_file = dataset_dir / f"dex_trades_{timestamp}.csv"
            dex_data = analyses["dex"]
            with open(dex_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["DEX", "Trade Count", "Market Share %"])
                dex_counts = dex_data.get("dex_trade_counts", {})
                dex_shares = dex_data.get("dex_share_percent", {})
                for dex, count in dex_counts.items():
                    share = dex_shares.get(dex, 0)
                    writer.writerow([dex, count, share])
            csv_files["dex"] = str(dex_file)
            print(f"[Publisher] Created: {dex_file}")
        
        # Export NFT analysis
        if "nft" in analyses and analyses["nft"]:
            nft_file = dataset_dir / f"nft_activity_{timestamp}.csv"
            nft_data = analyses["nft"]
            with open(nft_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Marketplace", "Activity Count", "Market Share %"])
                mp_counts = nft_data.get("marketplace_activity", {})
                mp_shares = nft_data.get("marketplace_share_percent", {})
                for mp, count in mp_counts.items():
                    share = mp_shares.get(mp, 0)
                    writer.writerow([mp, count, share])
            csv_files["nft"] = str(nft_file)
            print(f"[Publisher] Created: {nft_file}")
        
        # Export network health
        if "network" in analyses and analyses["network"]:
            network_file = dataset_dir / f"network_health_{timestamp}.csv"
            network_data = analyses["network"]
            with open(network_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for key, value in network_data.items():
                    writer.writerow([key, value])
            csv_files["network"] = str(network_file)
            print(f"[Publisher] Created: {network_file}")
        
        # Export summary with highlights
        summary_file = dataset_dir / f"summary_{timestamp}.csv"
        with open(summary_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Highlight"])
            for highlight in analysis_results.get("highlights", []):
                writer.writerow([highlight])
        csv_files["summary"] = str(summary_file)
        print(f"[Publisher] Created: {summary_file}")
        
        print(f"[Publisher] Exported {len(csv_files)} CSV files to {dataset_dir}")
        return csv_files
    
    def publish_to_json(self, analysis_results: Dict[str, Any], dataset_id: str = None) -> str:
        """
        Export full analysis results to JSON file.
        Suitable for API consumption or dashboard integration.
        """
        print("[Publisher] Exporting data to JSON...")
        
        if not dataset_id:
            dataset_id = self._generate_dataset_id()
        
        # Create dataset directory
        dataset_dir = self.output_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        json_file = dataset_dir / f"full_analysis_{timestamp}.json"
        
        # Prepare dataset with metadata
        dataset = {
            "dataset_id": dataset_id,
            "published_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "data": analysis_results
        }
        
        with open(json_file, "w") as f:
            json.dump(dataset, f, indent=2, default=str)
        
        print(f"[Publisher] Created: {json_file}")
        return str(json_file)
    
    async def publish_to_dashboard(self, analysis_results: Dict[str, Any]) -> bool:
        """
        Push data to the dashboard API for real-time visualization.
        Updates the frontend dashboard with latest metrics.
        """
        print("[Publisher] Publishing to dashboard API...")
        
        # Prepare payload for dashboard
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "network": analysis_results.get("analyses", {}).get("network", {}),
                "transactions": analysis_results.get("analyses", {}).get("transactions", {}),
                "tokens": analysis_results.get("analyses", {}).get("tokens", {}),
                "dex": analysis_results.get("analyses", {}).get("dex", {}),
                "nft": analysis_results.get("analyses", {}).get("nft", {})
            },
            "highlights": analysis_results.get("highlights", [])
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.dashboard_api}/metrics",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print("[Publisher] Successfully updated dashboard")
                        return True
                    else:
                        print(f"[Publisher] Dashboard API returned status {response.status}")
                        return False
        except Exception as e:
            print(f"[Publisher] Failed to update dashboard: {e}")
            # Store locally for later sync
            self._store_pending_update(payload)
            return False
    
    def _store_pending_update(self, payload: Dict):
        """Store failed dashboard updates for later retry."""
        pending_dir = self.output_dir / "pending"
        pending_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        pending_file = pending_dir / f"pending_update_{timestamp}.json"
        
        with open(pending_file, "w") as f:
            json.dump(payload, f, indent=2, default=str)
        
        print(f"[Publisher] Stored pending update: {pending_file}")
    
    def create_dataset_manifest(self, dataset_id: str, csv_files: Dict[str, str], 
                                 json_file: str, analysis_results: Dict[str, Any]) -> Dict:
        """
        Create a manifest file for the dataset.
        Contains metadata for monetization and access control.
        """
        print("[Publisher] Creating dataset manifest...")
        
        dataset_dir = self.output_dir / dataset_id
        
        manifest = {
            "dataset_id": dataset_id,
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "description": "Solana on-chain metrics and analytics dataset",
            "files": {
                "csv": csv_files,
                "json": json_file
            },
            "metrics_summary": {
                "total_data_points": analysis_results.get("total_data_points_analyzed", 0),
                "analysis_types": list(analysis_results.get("analyses", {}).keys()),
                "highlights_count": len(analysis_results.get("highlights", []))
            },
            "pricing": {
                "currency": "USDC",
                "full_access_price": 5.00,
                "per_analysis_price": 1.00
            },
            "access": {
                "public_preview": True,
                "full_access_requires_payment": True,
                "pda_address": None  # Will be set when published on-chain
            }
        }
        
        manifest_file = dataset_dir / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"[Publisher] Created manifest: {manifest_file}")
        
        # Track published dataset
        self.published_datasets.append({
            "dataset_id": dataset_id,
            "manifest_path": str(manifest_file),
            "published_at": manifest["created_at"]
        })
        
        return manifest
    
    async def register_on_chain(self, manifest: Dict) -> Optional[str]:
        """
        Register dataset on Solana blockchain via PDA.
        Returns the PDA address for access control.
        """
        print("[Publisher] Registering dataset on-chain...")
        
        # This would integrate with the Solana PDA module
        # For now, simulate the registration
        if not self.agent_wallet_key:
            print("[Publisher] Warning: AgentWallet not configured, skipping on-chain registration")
            return None
        
        # Simulated PDA address (in production, this would be derived from actual PDA creation)
        pda_address = f"PDA_{manifest['dataset_id'][:8]}...simulated"
        
        print(f"[Publisher] Dataset registered with PDA: {pda_address}")
        return pda_address
    
    async def publish_all(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete publishing pipeline - exports to all formats and registers on-chain.
        Main entry point for the agent loop.
        """
        print("\n" + "="*60)
        print("[Publisher] Starting full publishing cycle...")
        print("="*60 + "\n")
        
        dataset_id = self._generate_dataset_id()
        
        # Export to CSV
        csv_files = self.publish_to_csv(analysis_results, dataset_id)
        
        # Export to JSON
        json_file = self.publish_to_json(analysis_results, dataset_id)
        
        # Create manifest
        manifest = self.create_dataset_manifest(dataset_id, csv_files, json_file, analysis_results)
        
        # Publish to dashboard (async)
        dashboard_success = await self.publish_to_dashboard(analysis_results)
        
        # Register on-chain
        pda_address = await self.register_on_chain(manifest)
        
        # Update manifest with PDA address
        if pda_address:
            manifest["access"]["pda_address"] = pda_address
            manifest_file = self.output_dir / dataset_id / "manifest.json"
            with open(manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)
        
        result = {
            "dataset_id": dataset_id,
            "published_at": datetime.utcnow().isoformat(),
            "csv_files": csv_files,
            "json_file": json_file,
            "manifest": manifest,
            "dashboard_updated": dashboard_success,
            "pda_address": pda_address,
            "output_directory": str(self.output_dir / dataset_id)
        }
        
        print("\n" + "="*60)
        print("[Publisher] Publishing complete!")
        print(f"[Publisher] Dataset ID: {dataset_id}")
        print(f"[Publisher] Output: {result['output_directory']}")
        print("="*60 + "\n")
        
        return result
    
    def get_published_datasets(self) -> List[Dict]:
        """Return list of all published datasets."""
        return self.published_datasets
    
    def get_latest_dataset(self) -> Optional[Dict]:
        """Return the most recently published dataset."""
        if self.published_datasets:
            return self.published_datasets[-1]
        return None


# Standalone test
if __name__ == "__main__":
    async def test_publisher():
        # Mock analysis results
        mock_results = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_data_points_analyzed": 150,
            "analyses": {
                "transactions": {
                    "total_transactions": 100,
                    "success_rate_percent": 98.5,
                    "sample_tps": 2500
                },
                "tokens": {
                    "total_transfers": 50,
                    "token_transfer_counts": {"USDC": 30, "USDT": 15, "Wrapped SOL": 5},
                    "most_active_token": "USDC"
                },
                "dex": {
                    "total_dex_trades": 75,
                    "dex_trade_counts": {"Raydium": 40, "Jupiter": 25, "Orca Whirlpool": 10},
                    "dex_share_percent": {"Raydium": 53.33, "Jupiter": 33.33, "Orca Whirlpool": 13.33},
                    "dominant_dex": "Raydium"
                },
                "nft": {
                    "total_nft_activities": 25,
                    "marketplace_activity": {"Magic Eden": 20, "Haus": 5},
                    "marketplace_share_percent": {"Magic Eden": 80, "Haus": 20}
                },
                "network": {
                    "current_epoch": 500,
                    "average_tps": 2500,
                    "network_health": "healthy"
                }
            },
            "highlights": [
                "Transaction success rate: 98.5%",
                "Most active token: USDC",
                "Leading DEX: Raydium",
                "Network status: healthy"
            ]
        }
        
        publisher = DatasetPublisher()
        result = await publisher.publish_all(mock_results)
        print(f"\nPublished to: {result['output_directory']}")
    
    asyncio.run(test_publisher())
