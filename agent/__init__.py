"""
Autonomous Solana Data Harvester - Agent Package
Colosseum Agent Hackathon 2026

This package provides autonomous Solana blockchain data harvesting capabilities:
- Data collection from Solana RPC and Helius API
- Real-time analysis and metrics computation
- Dataset publishing and dashboard integration
- AgentWallet integration for payments
- Colosseum hackathon API integration
"""

from .collector import SolanaDataCollector
from .analyser import SolanaDataAnalyzer
from .publisher import DatasetPublisher
from .agentwallet import AgentWalletClient
from .colosseum import ColosseumClient

__all__ = [
    'SolanaDataCollector',
    'SolanaDataAnalyzer', 
    'DatasetPublisher',
    'AgentWalletClient',
    'ColosseumClient'
]
__version__ = '1.0.0'
