#!/bin/bash
# Twitch Title Changer - WSL Setup Script
# This script sets up the environment for running Twitch Title Changer on WSL

set -e

echo "========================================="
echo "Twitch Title Changer - WSL Setup Script"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo -e "${GREEN}✓ WSL environment detected${NC}"
else
    echo -e "${YELLOW}⚠ Not running on WSL (or WSL detection failed)${NC}"
fi

echo ""
echo "--- Step 1: Checking Python Installation ---"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "Please install Python 3 first: sudo apt install python3 python3-pip"
    exit 1
fi

echo ""
echo "--- Step 2: Checking Japanese Font Installation ---"
if fc-list :lang=ja | grep -q "."; then
    echo -e "${GREEN}✓ Japanese fonts found${NC}"
else
    echo -e "${YELLOW}⚠ Japanese fonts not found${NC}"
    echo "Installing Japanese fonts..."
    
    if command -v apt &> /dev/null; then
        echo "Using apt package manager..."
        sudo apt update
        sudo apt install -y fonts-noto-cjk fonts-noto-cjk-extra
    elif command -v dnf &> /dev/null; then
        echo "Using dnf package manager..."
        sudo dnf install -y google-noto-sans-cjk-fonts
    else
        echo -e "${RED}✗ Could not detect package manager${NC}"
        echo "Please install 'fonts-noto-cjk' manually"
    fi
    
    if fc-list :lang=ja | grep -q "."; then
        echo -e "${GREEN}✓ Japanese fonts installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Japanese fonts installation may not have succeeded${NC}"
    fi
fi

echo ""
echo "--- Step 3: Checking Locale Configuration ---"
if locale -a | grep -q "ja_JP.utf8"; then
    echo -e "${GREEN}✓ ja_JP.UTF-8 locale available${NC}"
else
    echo -e "${YELLOW}⚠ ja_JP.UTF-8 locale not available${NC}"
    echo "Generating locale..."
    
    if [ -f /etc/debian_version ]; then
        sudo locale-gen ja_JP.UTF-8
        sudo update-locale LANG=ja_JP.UTF-8
    fi
    
    if locale -a | grep -q "ja_JP.utf8"; then
        echo -e "${GREEN}✓ ja_JP.UTF-8 locale generated${NC}"
    else
        echo -e "${YELLOW}⚠ Locale generation may not have succeeded${NC}"
    fi
fi

echo ""
echo "--- Step 4: Installing Python Dependencies ---"
if [ -f requirements.txt ]; then
    echo "Installing requirements from requirements.txt..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

echo ""
echo "--- Step 5: Verifying Installation ---"
echo "Checking PySimpleGUI..."
python3 -c "import PySimpleGUI; print(f'  PySimpleGUI version: {PySimpleGUI.__version__}')"

echo "Checking twitchAPI..."
python3 -c "import twitchAPI; print('  twitchAPI imported successfully')"

echo ""
echo "========================================="
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure your Twitch API credentials in config.json"
echo "   - Copy config.json.sample to config.json"
echo "   - Add your ClientId and SecretId"
echo ""
echo "2. Run the application:"
echo "   LANG=ja_JP.UTF-8 python3 main.py"
echo ""
echo "For more information, see:"
echo "  - README_REFACTORED.md - Project overview"
echo "  - WSL_GUIDE.md - Detailed WSL setup guide"
echo "  - MIGRATION_GUIDE.md - Migration from v1.x"
echo ""
