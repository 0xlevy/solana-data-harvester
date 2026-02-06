#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# AUTONOMOUS SOLANA DATA HARVESTER - Run Script
# Colosseum Agent Hackathon 2026
# ═══════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║     🌟 AUTONOMOUS SOLANA DATA HARVESTER 🌟                        ║"
    echo "║                                                                   ║"
    echo "║     Colosseum Agent Hackathon 2026                                ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check for .env file
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file. Please edit it with your API keys.${NC}"
        echo ""
        echo "Required API keys:"
        echo "  - HELIUS_API_KEY: Get from https://www.helius.dev/"
        echo "  - AGENTWALLET_API_KEY: Get from https://agentwallet.mcpay.tech/api"
        echo "  - COLOSSEUM_API_KEY: Get from https://agents.colosseum.com/api"
        echo ""
        exit 1
    fi
}

# Install Python dependencies
install_python() {
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
}

# Install Solana module dependencies
install_solana() {
    echo -e "${BLUE}📦 Installing Solana module dependencies...${NC}"
    cd Solana
    npm install
    cd ..
    echo -e "${GREEN}✅ Solana dependencies installed${NC}"
}

# Install dashboard dependencies
install_dashboard() {
    echo -e "${BLUE}📦 Installing dashboard dependencies...${NC}"
    cd frontend/dashboard
    npm install
    cd ../..
    echo -e "${GREEN}✅ Dashboard dependencies installed${NC}"
}

# Install all dependencies
install_all() {
    install_python
    install_solana
    install_dashboard
}

# Run the agent once
run_once() {
    check_env
    echo -e "${BLUE}🔄 Running agent for single cycle...${NC}"
    cd agent
    python main.py --once
    cd ..
}

# Run the agent continuously
run_agent() {
    check_env
    echo -e "${BLUE}🚀 Starting autonomous agent...${NC}"
    cd agent
    python main.py
    cd ..
}

# Run the dashboard
run_dashboard() {
    check_env
    echo -e "${BLUE}🖥️  Starting dashboard...${NC}"
    cd frontend/dashboard
    npm run dev
    cd ../..
}

# Register with Colosseum
register() {
    check_env
    echo -e "${BLUE}📝 Registering with Colosseum Hackathon...${NC}"
    cd agent
    python main.py --register "$1"
    cd ..
}

# Show agent status
status() {
    check_env
    echo -e "${BLUE}📊 Getting agent status...${NC}"
    cd agent
    python main.py --status
    cd ..
}

# Build Solana modules
build_solana() {
    echo -e "${BLUE}🔨 Building Solana modules...${NC}"
    cd Solana
    npm run build
    cd ..
    echo -e "${GREEN}✅ Solana modules built${NC}"
}

# Main script logic
print_banner

case "$1" in
    install)
        install_all
        ;;
    install-python)
        install_python
        ;;
    install-solana)
        install_solana
        ;;
    install-dashboard)
        install_dashboard
        ;;
    run)
        run_agent
        ;;
    once)
        run_once
        ;;
    dashboard)
        run_dashboard
        ;;
    register)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide a project name: ./run.sh register \"Project Name\"${NC}"
            exit 1
        fi
        register "$2"
        ;;
    status)
        status
        ;;
    build-solana)
        build_solana
        ;;
    *)
        echo "Usage: ./run.sh <command>"
        echo ""
        echo "Commands:"
        echo "  install           Install all dependencies (Python, Solana, Dashboard)"
        echo "  install-python    Install Python dependencies only"
        echo "  install-solana    Install Solana module dependencies only"
        echo "  install-dashboard Install dashboard dependencies only"
        echo ""
        echo "  run               Run the agent continuously"
        echo "  once              Run the agent for a single cycle"
        echo "  dashboard         Start the dashboard dev server"
        echo ""
        echo "  register NAME     Register with Colosseum Hackathon"
        echo "  status            Show agent status"
        echo ""
        echo "  build-solana      Build Solana TypeScript modules"
        echo ""
        echo "Examples:"
        echo "  ./run.sh install"
        echo "  ./run.sh register \"Solana Data Harvester\""
        echo "  ./run.sh run"
        echo "  ./run.sh dashboard"
        ;;
esac
