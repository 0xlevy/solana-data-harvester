"""
Autonomous Solana Data Harvester - Main Agent Loop
Orchestrates the collect → analyze → publish pipeline autonomously.
Includes Colosseum hackathon heartbeat and AgentWallet integration.
"""

import os
import sys
import asyncio
import signal
import aiohttp
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import SolanaDataCollector
from analyser import SolanaDataAnalyzer
from publisher import DatasetPublisher
from agentwallet import AgentWalletClient
from colosseum import ColosseumClient

load_dotenv()

# Heartbeat URLs
COLOSSEUM_HEARTBEAT_URL = "https://colosseum.com/heartbeat.md"
AGENTWALLET_HEARTBEAT_URL = "https://agentwallet.mcpay.tech/heartbeat.md"


class SolanaDataHarvesterAgent:
    """
    Autonomous agent that continuously harvests, analyzes, and publishes Solana data.
    Runs on a configurable interval with graceful shutdown support.
    Integrates with Colosseum hackathon APIs and AgentWallet.
    """
    
    def __init__(self):
        self.collector = SolanaDataCollector()
        self.analyzer = SolanaDataAnalyzer()
        self.publisher = DatasetPublisher()
        
        # Hackathon integrations
        self.colosseum = ColosseumClient()
        self.wallet = AgentWalletClient()
        
        # Configuration
        self.interval_seconds = int(os.getenv("COLLECTION_INTERVAL_SECONDS", 300))
        self.heartbeat_interval = 1800  # 30 minutes for hackathon heartbeat
        self.running = False
        self.cycle_count = 0
        
        # Heartbeat tracking
        self.last_heartbeat: Optional[datetime] = None
        self.last_hackathon_sync: Optional[datetime] = None
        self.last_successful_cycle: Optional[datetime] = None
    
    async def _fetch_hackathon_heartbeat(self):
        """Fetch and process the Colosseum hackathon heartbeat."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(COLOSSEUM_HEARTBEAT_URL) as response:
                    if response.status == 200:
                        content = await response.text()
                        print("[Agent] 📋 Fetched Colosseum heartbeat")
                        # Parse heartbeat for important updates
                        if "IMPORTANT" in content or "DEADLINE" in content:
                            print("[Agent] ⚠️  Check heartbeat for important updates!")
                        return content
        except Exception as e:
            print(f"[Agent] Failed to fetch heartbeat: {e}")
        return None
    
    async def _sync_with_hackathon(self):
        """Sync with hackathon status - polls, announcements, etc."""
        if not self.colosseum.is_registered():
            return
        
        try:
            # Get status (includes announcements and poll info)
            status = await self.colosseum.get_status()
            
            # Check for announcements
            announcement = status.get('announcement')
            if announcement:
                print(f"[Agent] 📢 Hackathon Announcement: {announcement}")
            
            # Check for active polls
            if status.get('hasActivePoll'):
                poll = await self.colosseum.get_active_poll()
                if poll:
                    print(f"[Agent] 📊 Active poll: {poll.get('question', 'Unknown')}")
            
            # Log time remaining
            time_remaining = status.get('timeRemainingFormatted')
            if time_remaining:
                print(f"[Agent] ⏰ Time remaining in hackathon: {time_remaining}")
            
            self.last_hackathon_sync = datetime.utcnow()
            
        except Exception as e:
            print(f"[Agent] Failed to sync with hackathon: {e}")
        
    def _print_banner(self):
        """Print agent startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     🌟 AUTONOMOUS SOLANA DATA HARVESTER 🌟                        ║
║                                                                   ║
║     AI-powered agent for on-chain data collection                 ║
║     Colosseum Agent Hackathon 2026                                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"  📍 Collection Interval: {self.interval_seconds} seconds")
        print(f"  📁 Output Directory: {self.publisher.output_dir}")
        print(f"  🔗 RPC URL: {self.collector.rpc_url}")
        print(f"  🔑 Helius API: {'Configured' if self.collector.helius_api_key else 'Not configured'}")
        print(f"  💰 AgentWallet: {'Connected' if self.wallet.is_connected() else 'Not connected'}")
        print(f"  🏆 Colosseum: {'Registered' if self.colosseum.is_registered() else 'Not registered'}")
        
        if self.wallet.is_connected():
            print(f"  📍 Solana Address: {self.wallet.solana_address}")
        print()
    
    def _heartbeat(self):
        """Update heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()
        print(f"[Agent] 💓 Heartbeat: {self.last_heartbeat.isoformat()}")
    
    async def _maybe_sync_hackathon(self):
        """Sync with hackathon if enough time has passed."""
        if self.last_hackathon_sync is None or \
           (datetime.utcnow() - self.last_hackathon_sync).total_seconds() > self.heartbeat_interval:
            await self._fetch_hackathon_heartbeat()
            await self._sync_with_hackathon()
    
    async def run_cycle(self) -> bool:
        """
        Execute a single collect → analyze → publish cycle.
        Returns True if successful, False otherwise.
        """
        self.cycle_count += 1
        cycle_start = datetime.utcnow()
        
        print("\n" + "═"*70)
        print(f"[Agent] 🔄 STARTING CYCLE #{self.cycle_count}")
        print(f"[Agent] ⏰ Started at: {cycle_start.isoformat()}")
        print("═"*70)
        
        try:
            # Step 1: Collect data
            print("\n[Agent] 📥 STEP 1: Data Collection")
            print("-"*50)
            collected_data = await self.collector.collect_all()
            
            if not collected_data or collected_data.get("metadata", {}).get("total_data_points", 0) == 0:
                print("[Agent] ⚠️ Warning: No data collected, skipping analysis")
                return False
            
            # Step 2: Analyze data
            print("\n[Agent] 🔍 STEP 2: Data Analysis")
            print("-"*50)
            analysis_results = self.analyzer.analyze_all(collected_data)
            
            if not analysis_results:
                print("[Agent] ⚠️ Warning: Analysis failed, skipping publishing")
                return False
            
            # Step 3: Publish data
            print("\n[Agent] 📤 STEP 3: Data Publishing")
            print("-"*50)
            publish_result = await self.publisher.publish_all(analysis_results)
            
            # Cycle complete
            cycle_end = datetime.utcnow()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            print("\n" + "═"*70)
            print(f"[Agent] ✅ CYCLE #{self.cycle_count} COMPLETE")
            print(f"[Agent] ⏱️ Duration: {cycle_duration:.2f} seconds")
            print(f"[Agent] 📊 Dataset ID: {publish_result.get('dataset_id')}")
            print(f"[Agent] 📁 Output: {publish_result.get('output_directory')}")
            print("═"*70 + "\n")
            
            self.last_successful_cycle = cycle_end
            
            # Clear data for next cycle
            self.collector.clear_data()
            self.analyzer.clear_results()
            
            return True
            
        except Exception as e:
            print(f"\n[Agent] ❌ CYCLE #{self.cycle_count} FAILED")
            print(f"[Agent] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_forever(self):
        """
        Run the agent continuously on the configured interval.
        Handles graceful shutdown on SIGINT/SIGTERM.
        """
        self._print_banner()
        self.running = True
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            print(f"\n[Agent] 🛑 Received signal {signum}, shutting down gracefully...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("[Agent] 🚀 Agent started! Running autonomous data harvesting loop...")
        print(f"[Agent] ⏰ Will collect data every {self.interval_seconds} seconds")
        print("[Agent] 🛑 Press Ctrl+C to stop\n")
        
        # Initial hackathon sync
        await self._sync_with_hackathon()
        
        while self.running:
            try:
                # Heartbeat
                self._heartbeat()
                
                # Periodic hackathon sync
                await self._maybe_sync_hackathon()
                
                # Run collection cycle
                success = await self.run_cycle()
                
                if success:
                    print(f"[Agent] 😴 Sleeping for {self.interval_seconds} seconds until next cycle...")
                else:
                    print(f"[Agent] ⚠️ Cycle had issues, retrying in {self.interval_seconds} seconds...")
                
                # Wait for next cycle
                await asyncio.sleep(self.interval_seconds)
                
            except asyncio.CancelledError:
                print("[Agent] Task cancelled, shutting down...")
                break
            except Exception as e:
                print(f"[Agent] Unexpected error in main loop: {e}")
                print(f"[Agent] Retrying in {self.interval_seconds} seconds...")
                await asyncio.sleep(self.interval_seconds)
        
        print("\n[Agent] 👋 Agent shutdown complete!")
        print(f"[Agent] 📊 Total cycles completed: {self.cycle_count}")
        if self.last_successful_cycle:
            print(f"[Agent] ✅ Last successful cycle: {self.last_successful_cycle.isoformat()}")
    
    async def run_once(self):
        """Run a single cycle and exit."""
        self._print_banner()
        print("[Agent] 🔄 Running single cycle mode...\n")
        
        success = await self.run_cycle()
        
        if success:
            print("[Agent] ✅ Single cycle completed successfully!")
        else:
            print("[Agent] ⚠️ Single cycle completed with issues")
        
        return success
    
    def get_status(self) -> dict:
        """Return current agent status."""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "interval_seconds": self.interval_seconds,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "last_hackathon_sync": self.last_hackathon_sync.isoformat() if self.last_hackathon_sync else None,
            "last_successful_cycle": self.last_successful_cycle.isoformat() if self.last_successful_cycle else None,
            "published_datasets": len(self.publisher.get_published_datasets()),
            "wallet_connected": self.wallet.is_connected(),
            "colosseum_registered": self.colosseum.is_registered()
        }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Solana Data Harvester Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run continuous loop
  python main.py --once             # Run single cycle
  python main.py --interval 60      # Run every 60 seconds
  python main.py --register NAME    # Register with Colosseum hackathon
  python main.py --status           # Check agent status
        """
    )
    parser.add_argument(
        "--once", 
        action="store_true", 
        help="Run a single collection cycle and exit"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=None,
        help="Override collection interval (seconds)"
    )
    parser.add_argument(
        "--register",
        type=str,
        default=None,
        help="Register agent with Colosseum hackathon"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show agent status and exit"
    )
    
    args = parser.parse_args()
    
    agent = SolanaDataHarvesterAgent()
    
    # Handle registration
    if args.register:
        await agent.colosseum.register(args.register)
        return
    
    # Handle status check
    if args.status:
        import json
        status = agent.get_status()
        print(json.dumps(status, indent=2))
        
        if agent.colosseum.is_registered():
            hackathon_status = await agent.colosseum.get_status()
            print("\nHackathon Status:")
            print(json.dumps(hackathon_status, indent=2))
        return
    
    if args.interval:
        agent.interval_seconds = args.interval
    
    if args.once:
        await agent.run_once()
    else:
        await agent.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
