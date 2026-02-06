# Autonomous Solana Data Harvester - Demo

## 🎬 Demo Overview

This document showcases the key features and workflow of the Autonomous Solana Data Harvester.

---

## 📸 Screenshots

### Dashboard Overview
The main dashboard displays real-time Solana metrics including:
- Network health status and TPS
- Transaction success rates
- Token transfer activity
- DEX trading volumes
- NFT marketplace trends

![Dashboard Overview](./screenshots/dashboard.png)

### Network Stats Panel
Real-time network metrics showing:
- Current epoch and slot
- Average TPS (transactions per second)
- Epoch progress bar
- Circulating vs total SOL supply

### Transaction Analysis
Doughnut chart visualization showing:
- Successful vs failed transactions
- Overall success rate percentage
- Sample TPS in the center

### Token Activity
Horizontal bar chart displaying:
- Transfer counts per token (USDC, USDT, SOL, etc.)
- Most active token highlight
- Total transfer count

### DEX Trading Analysis
Pie chart showing DEX market share:
- Jupiter, Raydium, Orca Whirlpool distribution
- Trade counts per DEX
- Dominant DEX highlight

### NFT Marketplace Activity
Progress bars showing:
- Marketplace activity distribution
- Magic Eden, Tensor, Haus volumes
- Market share percentages

### Dataset Purchase
Cards for purchasing datasets with:
- Dataset description
- Price in USDC
- Data points count
- One-click USDC purchase via AgentWallet

---

## 🔄 Agent Workflow

### Collect Phase
```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     🌟 AUTONOMOUS SOLANA DATA HARVESTER 🌟                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

[Agent] 🚀 Agent started! Running autonomous data harvesting loop...
[Agent] ⏰ Will collect data every 300 seconds

═══════════════════════════════════════════════════════════════════
[Agent] 🔄 STARTING CYCLE #1
═══════════════════════════════════════════════════════════════════

[Agent] 📥 STEP 1: Data Collection
--------------------------------------------------
[Collector] Fetching 100 recent transactions...
[Collector] Fetching token transfers...
[Collector] Fetching NFT activity...
[Collector] Fetching DEX trades...
[Collector] Fetching network stats...
```

### Analyze Phase
```
[Agent] 🔍 STEP 2: Data Analysis
--------------------------------------------------
[Analyzer] Analyzing transactions...
[Analyzer] Transaction analysis complete - Success rate: 98.50%
[Analyzer] Analyzing token activity...
[Analyzer] Token analysis complete - 50 transfers across 3 tokens
[Analyzer] Analyzing NFT marketplace activity...
[Analyzer] NFT analysis complete - 25 activities tracked
[Analyzer] Analyzing DEX activity...
[Analyzer] DEX analysis complete - 75 trades across 3 DEXs
[Analyzer] Analyzing network health...
[Analyzer] Network analysis complete - Status: healthy
```

### Publish Phase
```
[Agent] 📤 STEP 3: Data Publishing
--------------------------------------------------
[Publisher] Exporting data to CSV files...
[Publisher] Created: ./data/dataset_20260206_120000/transactions_20260206_120000.csv
[Publisher] Created: ./data/dataset_20260206_120000/tokens_20260206_120000.csv
[Publisher] Created: ./data/dataset_20260206_120000/dex_trades_20260206_120000.csv
[Publisher] Created: ./data/dataset_20260206_120000/nft_activity_20260206_120000.csv
[Publisher] Created: ./data/dataset_20260206_120000/network_health_20260206_120000.csv
[Publisher] Exporting data to JSON...
[Publisher] Creating dataset manifest...
[Publisher] Publishing to dashboard API...
[Publisher] Registering dataset on-chain...

═══════════════════════════════════════════════════════════════════
[Agent] ✅ CYCLE #1 COMPLETE
[Agent] ⏱️ Duration: 4.23 seconds
[Agent] 📊 Dataset ID: dataset_20260206_120000
═══════════════════════════════════════════════════════════════════
```

---

## 📊 Sample Output Files

### CSV: transactions_20260206_120000.csv
```csv
Metric,Value
timestamp,2026-02-06T12:00:00.000Z
total_transactions,100
successful_transactions,98
failed_transactions,2
success_rate_percent,98.0
sample_tps,2500.5
slot_range,50
avg_tx_per_slot,2.0
```

### CSV: dex_trades_20260206_120000.csv
```csv
DEX,Trade Count,Market Share %
Raydium,40,53.33
Jupiter,25,33.33
Orca Whirlpool,10,13.33
```

### JSON: manifest.json
```json
{
  "dataset_id": "dataset_20260206_120000",
  "created_at": "2026-02-06T12:00:00.000Z",
  "version": "1.0",
  "description": "Solana on-chain metrics and analytics dataset",
  "pricing": {
    "currency": "USDC",
    "full_access_price": 5.00,
    "per_analysis_price": 1.00
  },
  "access": {
    "public_preview": true,
    "full_access_requires_payment": true,
    "pda_address": "PDA_dataset_..."
  }
}
```

---

## 🎯 Key Features Demonstrated

### 1. Autonomous Operation
- Agent runs continuously without human intervention
- Self-healing with retry logic on failures
- Configurable collection intervals

### 2. Multi-Source Data Collection
- Solana RPC for transactions and network stats
- Helius API for enhanced transaction data
- Multiple DEX and NFT marketplace tracking

### 3. Real-Time Analytics
- Transaction success rate analysis
- Token transfer volume tracking
- DEX market share calculation
- NFT marketplace dominance metrics

### 4. Multi-Format Export
- CSV files for spreadsheet analysis
- JSON for API consumption
- Dashboard API integration

### 5. On-Chain Monetization
- Datasets stored with PDA references
- USDC payments via AgentWallet
- Automated access control

---

## 🚀 Quick Start Demo

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (required)
# - HELIUS_API_KEY from https://www.helius.dev/
# - AGENTWALLET_API_KEY from https://agentwallet.mcpay.tech/api
# - COLOSSEUM_API_KEY from https://agents.colosseum.com/api
```

### 2. Install Dependencies
```bash
# Python agent
pip install -r requirements.txt

# Solana modules
cd Solana && npm install && cd ..

# Dashboard
cd frontend/dashboard && npm install && cd ..
```

### 3. Register with Colosseum Hackathon
```bash
cd agent
python main.py --register "Solana Data Harvester"
```

### 4. Check Status
```bash
cd agent
python main.py --status
```

### 5. Run the Agent (Single Cycle)
```bash
cd agent
python main.py --once
```

### 6. Run with Custom Interval
```bash
cd agent
python main.py --interval 60
```

### 7. Launch Dashboard
```bash
cd frontend/dashboard
npm run dev
# Open http://localhost:3000
```

---

## 📈 Metrics Highlights

| Metric | Sample Value |
|--------|--------------|
| Transactions Analyzed | 1,250 |
| Success Rate | 98.7% |
| Tokens Tracked | 4 |
| DEX Platforms | 4 |
| NFT Marketplaces | 3 |
| Average TPS | 2,847 |
| Datasets Published | 1 |

---

## 🔗 Links

- **Live Dashboard**: [Coming Soon]
- **Video Demo**: [YouTube - Coming Soon]
- **GitHub Repo**: [Repository Link]

---

*Built for Colosseum Agent Hackathon 2026*
