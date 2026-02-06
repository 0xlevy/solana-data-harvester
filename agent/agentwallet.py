"""
AgentWallet Integration Module
Provides wallet operations, transaction signing, and USDC payments via AgentWallet API.
This is the required wallet infrastructure for the Colosseum Agent Hackathon.

DO NOT manage raw Solana keys. Use AgentWallet instead.
"""

import os
import json
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# AgentWallet API Base URL
AGENTWALLET_API_BASE = "https://agentwallet.mcpay.tech/api"
AGENTWALLET_CONFIG_PATH = Path.home() / ".agentwallet" / "config.json"


@dataclass
class AgentWalletConfig:
    """AgentWallet configuration from ~/.agentwallet/config.json"""
    username: str
    email: str
    evm_address: str
    solana_address: str
    api_token: str
    moltbook_linked: bool = False
    moltbook_username: Optional[str] = None
    x_handle: Optional[str] = None


class AgentWalletClient:
    """
    AgentWallet client for Solana operations.
    Handles wallet creation, signing, transfers, and x402 payments.
    
    Usage:
        client = AgentWalletClient()
        if not client.is_connected():
            await client.connect(email="your@email.com")
        
        balance = await client.get_balances()
        await client.transfer_solana(to="...", amount=1000000, asset="usdc")
    """
    
    def __init__(self):
        self.config: Optional[AgentWalletConfig] = None
        self.api_base = AGENTWALLET_API_BASE
        self._load_config()
    
    def _load_config(self):
        """Load config from ~/.agentwallet/config.json if it exists."""
        if AGENTWALLET_CONFIG_PATH.exists():
            try:
                with open(AGENTWALLET_CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                self.config = AgentWalletConfig(
                    username=data.get('username', ''),
                    email=data.get('email', ''),
                    evm_address=data.get('evmAddress', ''),
                    solana_address=data.get('solanaAddress', ''),
                    api_token=data.get('apiToken', ''),
                    moltbook_linked=data.get('moltbookLinked', False),
                    moltbook_username=data.get('moltbookUsername'),
                    x_handle=data.get('xHandle')
                )
                print(f"[AgentWallet] Loaded config for user: {self.config.username}")
            except Exception as e:
                print(f"[AgentWallet] Failed to load config: {e}")
    
    def _save_config(self):
        """Save config to ~/.agentwallet/config.json"""
        if not self.config:
            return
        
        AGENTWALLET_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'username': self.config.username,
            'email': self.config.email,
            'evmAddress': self.config.evm_address,
            'solanaAddress': self.config.solana_address,
            'apiToken': self.config.api_token,
            'moltbookLinked': self.config.moltbook_linked,
            'moltbookUsername': self.config.moltbook_username,
            'xHandle': self.config.x_handle
        }
        
        with open(AGENTWALLET_CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Set secure permissions
        AGENTWALLET_CONFIG_PATH.chmod(0o600)
        print(f"[AgentWallet] Config saved to {AGENTWALLET_CONFIG_PATH}")
    
    def is_connected(self) -> bool:
        """Check if wallet is connected (has valid config with API token)."""
        return self.config is not None and bool(self.config.api_token)
    
    @property
    def username(self) -> Optional[str]:
        return self.config.username if self.config else None
    
    @property
    def solana_address(self) -> Optional[str]:
        return self.config.solana_address if self.config else None
    
    @property
    def evm_address(self) -> Optional[str]:
        return self.config.evm_address if self.config else None
    
    def _auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        if not self.config or not self.config.api_token:
            raise ValueError("AgentWallet not connected. Call connect() first.")
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }
    
    async def connect_start(self, email: str, referrer: Optional[str] = None) -> str:
        """
        Start the connection flow. Sends OTP to the provided email.
        Returns the username for the next step.
        """
        print(f"[AgentWallet] Starting connection for {email}...")
        
        payload = {"email": email}
        if referrer:
            payload["ref"] = referrer
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/connect/start",
                json=payload
            ) as response:
                data = await response.json()
                
                if not data.get('success', True):
                    raise ValueError(f"Connection failed: {data.get('error')}")
                
                username = data.get('username')
                print(f"[AgentWallet] OTP sent to {email}. Username: {username}")
                print("[AgentWallet] Ask user to check email and provide OTP.")
                return username
    
    async def connect_complete(self, username: str, email: str, otp: str) -> AgentWalletConfig:
        """
        Complete the connection flow with the OTP from email.
        Returns the wallet configuration.
        """
        print(f"[AgentWallet] Completing connection with OTP...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/connect/complete",
                json={
                    "username": username,
                    "email": email,
                    "otp": otp
                }
            ) as response:
                data = await response.json()
                
                if not data.get('success', True):
                    raise ValueError(f"Connection failed: {data.get('error')}")
                
                self.config = AgentWalletConfig(
                    username=username,
                    email=email,
                    evm_address=data.get('evmAddress', ''),
                    solana_address=data.get('solanaAddress', ''),
                    api_token=data.get('apiToken', ''),
                )
                
                self._save_config()
                print(f"[AgentWallet] Connected! Solana address: {self.config.solana_address}")
                return self.config
    
    async def get_balances(self) -> Dict[str, Any]:
        """Get wallet balances across all chains."""
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/wallets/{self.config.username}/balances",
                headers=self._auth_headers()
            ) as response:
                data = await response.json()
                return data
    
    async def get_solana_balance(self) -> Dict[str, float]:
        """Get Solana-specific balances (SOL and USDC)."""
        balances = await self.get_balances()
        
        solana_balances = {}
        for balance in balances.get('data', {}).get('balances', []):
            if 'solana' in balance.get('chain', '').lower():
                solana_balances[balance.get('asset', 'unknown')] = float(balance.get('amount', 0))
        
        return solana_balances
    
    async def transfer_solana(
        self,
        to: str,
        amount: int,
        asset: str = "usdc",
        network: str = "mainnet",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer SOL or USDC on Solana.
        
        Args:
            to: Recipient Solana address
            amount: Amount in smallest units (SOL: 9 decimals, USDC: 6 decimals)
            asset: "sol" or "usdc"
            network: "mainnet" or "devnet"
            idempotency_key: Optional key for deduplication
        
        Returns:
            Transaction result with actionId, status, txHash, explorer URL
        """
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        payload = {
            "to": to,
            "amount": str(amount),
            "asset": asset,
            "network": network
        }
        
        if idempotency_key:
            payload["idempotencyKey"] = idempotency_key
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/wallets/{self.config.username}/actions/transfer-solana",
                headers=self._auth_headers(),
                json=payload
            ) as response:
                data = await response.json()
                
                if not data.get('success', True):
                    raise ValueError(f"Transfer failed: {data.get('error')}")
                
                print(f"[AgentWallet] Transfer complete: {data.get('txHash')}")
                return data
    
    async def request_devnet_sol(self) -> Dict[str, Any]:
        """
        Request devnet SOL from faucet (0.1 SOL).
        Rate limited to 3 requests per 24 hours.
        """
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/wallets/{self.config.username}/actions/faucet-sol",
                headers=self._auth_headers(),
                json={}
            ) as response:
                data = await response.json()
                
                if not data.get('success', True):
                    raise ValueError(f"Faucet failed: {data.get('error')}")
                
                print(f"[AgentWallet] Received 0.1 devnet SOL. Remaining: {data.get('remaining')}")
                return data
    
    async def sign_message(self, message: str, chain: str = "solana") -> Dict[str, Any]:
        """
        Sign a message with the wallet.
        
        Args:
            message: Message to sign
            chain: "solana" or "evm"
        
        Returns:
            Signature result
        """
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/wallets/{self.config.username}/actions/sign-message",
                headers=self._auth_headers(),
                json={
                    "chain": chain,
                    "message": message
                }
            ) as response:
                data = await response.json()
                return data
    
    async def x402_fetch(
        self,
        url: str,
        method: str = "GET",
        body: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        preferred_chain: str = "auto",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Make an x402 payment-enabled API call.
        Handles 402 detection, payment signing, and retry automatically.
        
        Args:
            url: Target API URL (must be HTTPS in production)
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            body: Request body (auto-serialized to JSON)
            headers: Additional headers
            preferred_chain: "auto", "evm", or "solana"
            dry_run: Preview payment cost without paying
        
        Returns:
            API response with payment details
        """
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        payload = {
            "url": url,
            "method": method,
            "preferredChain": preferred_chain,
            "dryRun": dry_run
        }
        
        if body:
            payload["body"] = body
        if headers:
            payload["headers"] = headers
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/wallets/{self.config.username}/actions/x402/fetch",
                headers=self._auth_headers(),
                json=payload
            ) as response:
                data = await response.json()
                return data
    
    async def get_activity(self, limit: int = 50) -> Dict[str, Any]:
        """Get wallet activity history."""
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/wallets/{self.config.username}/activity?limit={limit}",
                headers=self._auth_headers()
            ) as response:
                return await response.json()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get personal wallet stats (rank, volume, streak)."""
        if not self.is_connected():
            raise ValueError("AgentWallet not connected")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/wallets/{self.config.username}/stats",
                headers=self._auth_headers()
            ) as response:
                return await response.json()
    
    def get_funding_url(self) -> str:
        """Get URL for funding the wallet via Coinbase Onramp."""
        if not self.config:
            raise ValueError("AgentWallet not connected")
        return f"https://agentwallet.mcpay.tech/u/{self.config.username}"


# Convenience function for quick setup
async def setup_agentwallet(email: str, otp: Optional[str] = None) -> AgentWalletClient:
    """
    Quick setup for AgentWallet.
    
    If config exists, returns connected client.
    If otp is provided, completes connection.
    Otherwise, starts connection flow.
    """
    client = AgentWalletClient()
    
    if client.is_connected():
        print(f"[AgentWallet] Already connected as {client.username}")
        return client
    
    if otp:
        # Assume we have a pending connection
        # This would need the username from connect_start
        print("[AgentWallet] OTP provided but no pending connection")
        raise ValueError("Start connection with connect_start() first")
    
    # Start connection flow
    username = await client.connect_start(email)
    print(f"[AgentWallet] Check email for OTP, then call:")
    print(f"  await client.connect_complete('{username}', '{email}', 'YOUR_OTP')")
    
    return client


# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = AgentWalletClient()
        
        if client.is_connected():
            print(f"Connected as: {client.username}")
            print(f"Solana address: {client.solana_address}")
            
            balances = await client.get_balances()
            print(f"Balances: {balances}")
        else:
            print("Not connected. Run setup flow with email.")
    
    asyncio.run(test())
