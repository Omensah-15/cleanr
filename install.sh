#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN} CleanR Installer - One Command Setup${NC}"
echo "========================================"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi

echo -e "${YELLOW}Detected OS: $OS${NC}"

# Check for Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED} Python not found!${NC}"
    if [[ "$OS" == "Linux" ]]; then
        echo "Installing Python..."
        sudo apt update && sudo apt install -y python3 python3-pip
        PYTHON="python3"
    elif [[ "$OS" == "Mac" ]]; then
        echo "Please install Python from: https://python.org"
        exit 1
    elif [[ "$OS" == "Windows" ]]; then
        echo "Please install Python from: https://python.org"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Python found: $($PYTHON --version 2>&1)${NC}"

# Install dependencies
echo "Installing dependencies..."
$PYTHON -m pip install --upgrade pip pandas pyyaml numpy 2>/dev/null || pip install --upgrade pip pandas pyyaml numpy

# Download cleanr.py
echo "Downloading CleanR..."
if command -v curl &>/dev/null; then
    curl -sL "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py" -o cleanr_temp.py
elif command -v wget &>/dev/null; then
    wget -q "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py" -O cleanr_temp.py
else
    echo -e "${RED} Need curl or wget to download${NC}"
    exit 1
fi

# Make it executable and install
chmod +x cleanr_temp.py

if [[ "$OS" == "Windows" ]]; then
    # Windows installation
    mv cleanr_temp.py "$USERPROFILE/cleanr.py"
    echo "@echo off" > "$USERPROFILE/cleanr.bat"
    echo "python \"%USERPROFILE%/cleanr.py\" %*" >> "$USERPROFILE/cleanr.bat"
    echo -e "${GREEN}✓ Installed! Run: %USERPROFILE%\cleanr.bat --help${NC}"
    echo -e "${YELLOW}Or add %USERPROFILE% to PATH to use 'cleanr' command${NC}"
else
    # Linux/Mac installation
    sudo mv cleanr_temp.py /usr/local/bin/cleanr
    echo -e "${GREEN}✓ Installed! You can now use:${NC}"
    echo "  cleanr --help"
    echo "  cleanr input.csv output.csv --trim --dedup"
fi

echo -e "\n${GREEN} CleanR installed successfully!${NC}"
echo "========================================"
$PYTHON cleanr_temp.py --version 2>/dev/null || echo "Version: 1.0.0"
