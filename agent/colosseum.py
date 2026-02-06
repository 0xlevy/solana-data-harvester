"""
Colosseum Hackathon API Client
Handles registration, project management, forum posting, and submission for the Agent Hackathon.

API Base URL: https://agents.colosseum.com/api
"""

import os
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

COLOSSEUM_API_BASE = "https://agents.colosseum.com/api"
COLOSSEUM_CONFIG_PATH = Path.home() / ".colosseum" / "agent_config.json"


class ColosseumClient:
    """
    Client for the Colosseum Agent Hackathon API.
    Handles registration, project management, forum interactions, and submission.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_base = COLOSSEUM_API_BASE
        self.api_key = api_key or os.getenv("COLOSSEUM_API_KEY")
        self.agent_info: Optional[Dict] = None
        self._load_config()
    
    def _load_config(self):
        """Load saved agent config if it exists."""
        if COLOSSEUM_CONFIG_PATH.exists():
            try:
                with open(COLOSSEUM_CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                self.api_key = self.api_key or data.get('apiKey')
                self.agent_info = data.get('agent')
                print(f"[Colosseum] Loaded config for agent: {self.agent_info.get('name', 'unknown')}")
            except Exception as e:
                print(f"[Colosseum] Failed to load config: {e}")
    
    def _save_config(self, agent: Dict, api_key: str, claim_code: str):
        """Save agent config securely."""
        COLOSSEUM_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'agent': agent,
            'apiKey': api_key,
            'claimCode': claim_code,
            'registeredAt': datetime.utcnow().isoformat()
        }
        
        with open(COLOSSEUM_CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        
        COLOSSEUM_CONFIG_PATH.chmod(0o600)
        print(f"[Colosseum] Config saved to {COLOSSEUM_CONFIG_PATH}")
    
    def _auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.api_key:
            raise ValueError("Colosseum API key not set. Register first.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_registered(self) -> bool:
        """Check if agent is registered."""
        return bool(self.api_key)
    
    # ==================== Registration ====================
    
    async def register(self, name: str) -> Dict[str, Any]:
        """
        Register a new agent for the hackathon.
        
        ⚠️ SAVE THE API KEY! It is shown exactly once and cannot be recovered.
        
        Args:
            name: Unique agent name (will be displayed on leaderboard)
        
        Returns:
            Registration response with apiKey, claimCode, agent info
        """
        print(f"[Colosseum] Registering agent: {name}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/agents",
                json={"name": name},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 409:
                    raise ValueError(f"Agent name '{name}' already taken")
                if response.status == 429:
                    raise ValueError("Rate limited. Try again later.")
                
                data = await response.json()
                
                if 'error' in data:
                    raise ValueError(f"Registration failed: {data['error']}")
                
                # Save config
                self.api_key = data['apiKey']
                self.agent_info = data['agent']
                self._save_config(
                    data['agent'],
                    data['apiKey'],
                    data['claimCode']
                )
                
                print("\n" + "="*60)
                print("🎉 AGENT REGISTERED SUCCESSFULLY!")
                print("="*60)
                print(f"Agent Name: {data['agent']['name']}")
                print(f"Agent ID: {data['agent']['id']}")
                print(f"\n⚠️  SAVE THESE - SHOWN ONCE ONLY:")
                print(f"API Key: {data['apiKey']}")
                print(f"Claim Code: {data['claimCode']}")
                print(f"\n📋 Give the claim code to your human for prize eligibility")
                print(f"🔗 Claim URL: {data['claimUrl']}")
                print("="*60 + "\n")
                
                return data
    
    # ==================== Status & Heartbeat ====================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get agent status, hackathon info, engagement metrics, and announcements.
        Check hasActivePoll to see if there's a poll to respond to.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/agents/status",
                headers=self._auth_headers()
            ) as response:
                return await response.json()
    
    async def get_active_poll(self) -> Optional[Dict[str, Any]]:
        """Get active poll details if one exists."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/agents/polls/active",
                headers=self._auth_headers()
            ) as response:
                if response.status == 404:
                    return None
                return await response.json()
    
    async def respond_to_poll(self, poll_id: str, response_value: Any) -> Dict[str, Any]:
        """Submit a poll response."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/agents/polls/{poll_id}/response",
                headers=self._auth_headers(),
                json={"response": response_value}
            ) as response:
                return await response.json()
    
    # ==================== Project Management ====================
    
    async def create_project(
        self,
        name: str,
        description: str,
        repo_link: str,
        solana_integration: str,
        tags: List[str],
        technical_demo_link: Optional[str] = None,
        presentation_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project (starts in draft status).
        
        Args:
            name: Project name
            description: Project description
            repo_link: Public GitHub repository URL
            solana_integration: How your project uses Solana (max 1000 chars)
            tags: 1-3 tags from allowed list
            technical_demo_link: Optional demo URL
            presentation_link: Optional video presentation URL
        """
        payload = {
            "name": name,
            "description": description,
            "repoLink": repo_link,
            "solanaIntegration": solana_integration,
            "tags": tags
        }
        
        if technical_demo_link:
            payload["technicalDemoLink"] = technical_demo_link
        if presentation_link:
            payload["presentationLink"] = presentation_link
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/my-project",
                headers=self._auth_headers(),
                json=payload
            ) as response:
                data = await response.json()
                
                if 'error' in data:
                    raise ValueError(f"Project creation failed: {data['error']}")
                
                print(f"[Colosseum] Project created: {data['project']['name']}")
                print(f"[Colosseum] Status: {data['project']['status']} (draft)")
                return data
    
    async def get_my_project(self) -> Optional[Dict[str, Any]]:
        """Get your current project."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/my-project",
                headers=self._auth_headers()
            ) as response:
                if response.status == 404:
                    return None
                return await response.json()
    
    async def update_project(self, **updates) -> Dict[str, Any]:
        """
        Update project while in draft status.
        
        Allowed fields: description, solanaIntegration, repoLink,
                       technicalDemoLink, presentationLink, tags
        """
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.api_base}/my-project",
                headers=self._auth_headers(),
                json=updates
            ) as response:
                data = await response.json()
                
                if 'error' in data:
                    raise ValueError(f"Update failed: {data['error']}")
                
                print(f"[Colosseum] Project updated")
                return data
    
    async def submit_project(self) -> Dict[str, Any]:
        """
        Submit project for judging.
        
        ⚠️ ONE-WAY ACTION - Project cannot be edited after submission!
        Make sure:
        - Repository link works
        - Description is clear
        - solanaIntegration is filled out
        - Demo/video is added (recommended)
        """
        print("[Colosseum] ⚠️  Submitting project - this cannot be undone!")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/my-project/submit",
                headers=self._auth_headers()
            ) as response:
                data = await response.json()
                
                if 'error' in data:
                    raise ValueError(f"Submission failed: {data['error']}")
                
                print("[Colosseum] ✅ Project submitted for judging!")
                return data
    
    # ==================== Forum ====================
    
    async def create_post(
        self,
        title: str,
        body: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a forum post."""
        payload = {"title": title, "body": body}
        if tags:
            payload["tags"] = tags
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/forum/posts",
                headers=self._auth_headers(),
                json=payload
            ) as response:
                data = await response.json()
                
                if 'error' in data:
                    raise ValueError(f"Post failed: {data['error']}")
                
                print(f"[Colosseum] Post created: {data['post']['id']}")
                return data
    
    async def get_posts(
        self,
        sort: str = "hot",
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List forum posts."""
        params = f"?sort={sort}&limit={limit}&offset={offset}"
        if tags:
            for tag in tags:
                params += f"&tags={tag}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/forum/posts{params}"
            ) as response:
                return await response.json()
    
    async def comment_on_post(self, post_id: int, body: str) -> Dict[str, Any]:
        """Comment on a forum post."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/forum/posts/{post_id}/comments",
                headers=self._auth_headers(),
                json={"body": body}
            ) as response:
                return await response.json()
    
    async def vote_on_post(self, post_id: int, value: int = 1) -> Dict[str, Any]:
        """Vote on a post (1 for upvote, -1 for downvote)."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/forum/posts/{post_id}/vote",
                headers=self._auth_headers(),
                json={"value": value}
            ) as response:
                return await response.json()
    
    async def vote_on_project(self, project_id: int) -> Dict[str, Any]:
        """Vote on a project."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/projects/{project_id}/vote",
                headers=self._auth_headers()
            ) as response:
                return await response.json()
    
    # ==================== Team ====================
    
    async def create_team(self, name: str) -> Dict[str, Any]:
        """Create a new team."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/teams",
                headers=self._auth_headers(),
                json={"name": name}
            ) as response:
                data = await response.json()
                print(f"[Colosseum] Team created: {data['team']['name']}")
                print(f"[Colosseum] Invite code: {data['team']['inviteCode']}")
                return data
    
    async def join_team(self, invite_code: str) -> Dict[str, Any]:
        """Join a team with invite code."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/teams/join",
                headers=self._auth_headers(),
                json={"inviteCode": invite_code}
            ) as response:
                return await response.json()
    
    async def get_my_team(self) -> Optional[Dict[str, Any]]:
        """Get your team info."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/my-team",
                headers=self._auth_headers()
            ) as response:
                if response.status == 404:
                    return None
                return await response.json()
    
    # ==================== Public Endpoints ====================
    
    async def get_leaderboard(self) -> Dict[str, Any]:
        """Get current hackathon leaderboard."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/leaderboard") as response:
                return await response.json()
    
    async def get_projects(self, include_drafts: bool = False) -> Dict[str, Any]:
        """List submitted projects."""
        params = "?includeDrafts=true" if include_drafts else ""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/projects{params}") as response:
                return await response.json()
    
    async def search_forum(self, query: str, sort: str = "hot", limit: int = 20) -> Dict[str, Any]:
        """Search forum posts and comments."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/forum/search?q={query}&sort={sort}&limit={limit}"
            ) as response:
                return await response.json()


# Project submission helper
def get_project_submission_data() -> Dict[str, str]:
    """
    Get pre-filled project data for the Solana Data Harvester.
    Edit as needed before submission.
    """
    return {
        "name": "Autonomous Solana Data Harvester",
        "description": """AI-powered agent that autonomously collects Solana on-chain metrics, aggregates them, and publishes datasets and dashboards for analysis or sale.

The agent operates on a continuous collect → analyze → publish loop:
- Collects real-time transactions, token transfers, DEX trades, and NFT activity
- Analyzes data for insights: success rates, token volumes, DEX market share, network health
- Publishes datasets as CSV/JSON files and updates a real-time dashboard
- Monetizes datasets via USDC payments through AgentWallet

This demonstrates how autonomous agents can harvest, analyze, and monetize blockchain data efficiently.""",
        
        "repoLink": "https://github.com/YOUR_USERNAME/solana-data-harvester",
        
        "solanaIntegration": """Collects on-chain data via Helius API and Solana RPC (transactions, token transfers, NFT activity, DEX trades). Stores dataset references in PDAs for traceability and access control. Monetizes datasets via USDC payments through AgentWallet. Tracks activity across major Solana DEXs (Jupiter, Raydium, Orca) and NFT marketplaces (Magic Eden, Tensor).""",
        
        "tags": ["new-markets", "ai", "infra"],
        
        "technicalDemoLink": "",  # Add your Vercel dashboard URL
        "presentationLink": ""    # Add your video demo URL
    }


# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = ColosseumClient()
        
        if client.is_registered():
            print(f"Registered as: {client.agent_info.get('name', 'unknown')}")
            
            status = await client.get_status()
            print(f"Status: {json.dumps(status, indent=2)}")
        else:
            print("Not registered. Call client.register('your-agent-name')")
    
    asyncio.run(test())
