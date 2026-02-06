# Autonomous Solana Data Harvester

![Project Banner](./demo/logo.png)

**AI-powered autonomous agent that collects Solana on-chain metrics, analyzes them, and publishes datasets and dashboards for analysis or sale.**

**Hackathon:** Colosseum Agent Hackathon 2026  
**Prize Pool:** $100,000 USDC

---

## 🚀 Overview

The **Autonomous Solana Data Harvester** is an AI-driven agent designed to operate fully autonomously on the Solana blockchain. It:

- Collects real-time on-chain data (transactions, token transfers, DEX trades, NFTs) via **Helius API** and Solana RPC
- Aggregates and analyzes datasets for meaningful insights
- Publishes metrics and dashboards for visualization and sale in **USDC**, using **AgentWallet** and on-chain PDAs for secure access
- Operates continuously and autonomously, with minimal human intervention
- Syncs with Colosseum hackathon heartbeat for announcements and polls

This project demonstrates how autonomous agents can **harvest, analyze, and monetize blockchain data** efficiently.

---

## 💡 Problem Statement

On-chain metrics are abundant, but accessing, aggregating, and visualizing them is **time-consuming, fragmented, and costly**.

**Challenges:**
- Developers and traders need **real-time insights** from Solana data
- On-chain analytics dashboards are often **centralized or slow**
- Monetizing datasets requires **secure, auditable transactions**

**Our solution:** An agent that **automates the entire process** — collection, aggregation, visualization, and monetization — **on-chain and in real-time**.

---

## 🧩 Features

### Core Agent Capabilities
- Fetch recent transactions, token transfers, and NFT activity
- Aggregate metrics like token volume, popular mints, DEX swaps
- Store datasets securely on Solana **PDAs** for traceability
- Publish CSV or dashboard datasets for sale or public access

### Dashboard
- Web-based visualization using **Next.js** and **Chart.js**
- Displays token activity, trading volume, and analytics trends
- Real-time updates with network health indicators

### Monetization
- Users can purchase datasets in **USDC**
- Transactions managed via **AgentWallet** and escrow PDAs
- Automated access control ensures only paying users can retrieve datasets

### Automation
- Agent runs on a loop: `collect → analyze → publish`
- Heartbeat syncs with Colosseum hackathon events and updates
- Graceful shutdown with signal handling

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Agent & Collector | Python 3.11, aiohttp, Pandas, asyncio |
| On-chain Solana | PDAs, AgentWallet, Helius API |
| Frontend Dashboard | Next.js 14, React, Chart.js, Tailwind CSS |
| Payment & Escrow | USDC, AgentWallet, Solana PDAs |
| APIs | Colosseum API, AgentWallet API |

---

## ⚡ Architecture

```
+------------------+          +-------------------+          +------------------+
| Solana Blockchain| <------> | Helius RPC/Webhook| <------> | Agent Collector  |
+------------------+          +-------------------+          +------------------+
        |                                                           |
        |                                                           v
        |                                                  +------------------+
        |                                                  | Data Analyzer    |
        |                                                  +------------------+
        |                                                           |
        |                                                           v
        |                                                  +------------------+
        |                                                  | Dataset Publisher|
        |                                                  +------------------+
        |                                                           |
        v                                                           v
+------------------+                                      +------------------+
| AgentWallet PDAs |                                      | Frontend Dashboard|
| (Payment/Escrow) |                                      |  & CSV Exports   |
+------------------+                                      +------------------+
```

**Flow:**
1. Agent fetches real-time transactions from Solana using Helius
2. Analyzer aggregates metrics (volume, token activity, trends)
3. Publisher writes datasets to PDAs and optionally CSV or dashboards
4. Users purchase dataset access via **USDC**, processed securely by **AgentWallet**

---

## 📁 Project Structure

```
/agent
  collector.py       # Collect Solana on-chain data
  analyser.py        # Aggregate and process metrics
  publisher.py       # Publish datasets and dashboards
  main.py            # Agent loop with hackathon sync
  agentwallet.py     # AgentWallet integration
  colosseum.py       # Colosseum hackathon API client

/Solana
  pdas.ts            # PDA management
  escrow.ts          # USDC payments & access control
  index.ts           # Module exports

/frontend/dashboard
  src/               # Next.js dashboard application
  components/        # React components

/demo
  demo.md            # Screenshots, workflow, demo guide

.env.example         # Environment variable template
requirements.txt     # Python dependencies
run.sh              # Convenience run script
```

---

## ⚙️ Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/solana-data-harvester.git
cd solana-data-harvester
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - HELIUS_API_KEY from https://www.helius.dev/
# - AGENTWALLET_API_KEY from https://agentwallet.mcpay.tech/api
# - COLOSSEUM_API_KEY from https://agents.colosseum.com/api
```

### 3. Install Dependencies
```bash
# Use the convenience script
./run.sh install

# Or manually:
pip install -r requirements.txt
cd Solana && npm install && cd ..
cd frontend/dashboard && npm install && cd ..
```

### 4. Register with Hackathon
```bash
./run.sh register "Solana Data Harvester"
# Or: cd agent && python main.py --register "Solana Data Harvester"
```

### 5. Run the Agent
```bash
# Run continuously
./run.sh run

# Or run single cycle
./run.sh once

# Or manually:
cd agent && python main.py
```

### 6. Launch Dashboard
```bash
./run.sh dashboard
# Or: cd frontend/dashboard && npm run dev
# Visit http://localhost:3000
```

---

## 🎯 Usage Examples

### Run agent with custom interval
```bash
cd agent
python main.py --interval 60  # Collect every 60 seconds
```

### Check agent status
```bash
cd agent
python main.py --status
```

### Single collection cycle
```bash
cd agent
python main.py --once
```

---

## 📊 Demo

See [demo/demo.md](demo/demo.md) for:
- Screenshots and visualizations
- Sample output files
- Agent workflow examples
- Quick start guide

---

## 🛡 Security

- **Never commit private keys or API keys**. Use `.env` for local development.
- Payments and access handled via **AgentWallet PDAs** — no raw key management required.
- Agent is fully autonomous; humans do not handle private Solana keys.
- All sensitive configuration via environment variables.

---

## 🏆 Hackathon Submission

| Field | Value |
|-------|-------|
| **Project Status** | Completed |
| **Category Tags** | `new-markets`, `ai`, `infra` |
| **Solana Integration** | Helius API for enhanced RPC, PDAs for dataset storage, AgentWallet for secure USDC payments |
| **Autonomy** | Fully autonomous collect → analyze → publish loop |

### Key Differentiators
1. **True Autonomy** - Runs without human intervention
2. **On-chain Monetization** - USDC payments via AgentWallet
3. **Real-time Analytics** - Live dashboard with Chart.js
4. **Hackathon Integration** - Syncs with Colosseum heartbeat

---

## 📌 Roadmap

1. ✅ Core agent functionality (collect, analyze, publish)
2. ✅ AgentWallet integration for payments
3. ✅ Colosseum hackathon API integration
4. ✅ Real-time dashboard with Chart.js
5. 🔜 AI trend prediction module
6. 🔜 Multi-agent collaboration
7. 🔜 Subscription-based dataset access

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📜 License

MIT License © 2026 Autonomous Solana Data Harvester Team

---

## 🔗 Links

- **Colosseum Hackathon:** https://agents.colosseum.com
- **AgentWallet Docs:** https://agentwallet.mcpay.tech/api
- **Helius API:** https://www.helius.dev
- **Live Dashboard:** Coming Soon

---

*Built with ❤️ for Colosseum Agent Hackathon 2026*
