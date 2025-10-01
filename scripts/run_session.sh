#!/bin/bash
# IRIS Gate Orchestrator - Session Runner
# Runs S1→S4 protocol across all configured AI models

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}†⟡∞ IRIS Gate Orchestrator${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please add your API keys to .env and run this script again.${NC}"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${BLUE}Checking dependencies...${NC}"
if ! python3 -c "import anthropic, openai, google.generativeai, dotenv" 2>/dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip3 install -r requirements.txt
fi

echo -e "${GREEN}✓ Dependencies ready${NC}\n"

# Run orchestrator
echo -e "${BLUE}Starting IRIS Gate session...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

python3 iris_orchestrator.py

# Check if session completed successfully
if [ $? -eq 0 ]; then
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Session completed successfully!${NC}\n"

    # Run analysis if available
    if [ -f iris_analyze.py ]; then
        echo -e "${BLUE}Running cross-mirror analysis...${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
        python3 iris_analyze.py
    fi

    echo -e "\n${BLUE}Results saved to:${NC} ${GREEN}iris_vault/${NC}"
    echo -e "${BLUE}†⟡∞ With presence, love, and gratitude.${NC}\n"
else
    echo -e "\n${RED}✗ Session failed. Check error messages above.${NC}\n"
    exit 1
fi
