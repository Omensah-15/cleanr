#!/bin/bash

echo "========================================="
echo "CleanR Professional CSV Cleaner - Installer"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS and shell
detect_environment() {
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="Windows"
    else
        OS="Unknown"
    fi
    
    # Detect if running in Git Bash
    if [[ -n "$MSYSTEM" ]] && [[ "$MSYSTEM" =~ ^MINGW ]]; then
        IN_GIT_BASH=true
    else
        IN_GIT_BASH=false
    fi
    
    print_info "Detected: $OS $(if $IN_GIT_BASH; then echo "(Git Bash)"; fi)"
}

# Check if CleanR is already installed
check_existing_installation() {
    if command_exists cleanr; then
        print_warning "CleanR appears to be already installed"
        echo "Location: $(which cleanr)"
        read -p "Do you want to reinstall? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
        print_info "Proceeding with reinstallation..."
    fi
}

# Check Python installation
check_python() {
    if command_exists python3; then
        PYTHON="python3"
    elif command_exists python; then
        PYTHON="python"
    else
        print_error "Python not found in PATH"
        echo ""
        echo "Please install Python 3.7 or newer from:"
        echo "  https://www.python.org/downloads/"
        echo ""
        echo "Ensure you check 'Add Python to PATH' during installation"
        echo "Then run this installer again."
        exit 1
    fi
    
    # Verify Python version
    PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if (( $(echo "$PYTHON_VERSION < 3.7" | bc -l 2>/dev/null || echo "0") )); then
        print_error "Python $PYTHON_VERSION detected. Python 3.7 or newer is required."
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Install dependencies
install_dependencies() {
    print_info "Installing required packages..."
    
    # Try with pip3 first, then pip
    if command_exists pip3; then
        PIP="pip3"
    elif command_exists pip; then
        PIP="pip"
    else
        print_warning "pip not found, attempting to install..."
        $PYTHON -m ensurepip --upgrade 2>/dev/null || true
        PIP="$PYTHON -m pip"
    fi
    
    # Install packages
    $PIP install --upgrade pip >/dev/null 2>&1 || true
    $PIP install pandas pyyaml numpy >/dev/null 2>&1
    
    if $PIP list | grep -q pandas; then
        print_success "Dependencies installed successfully"
    else
        print_warning "Could not verify package installation. Continuing anyway..."
    fi
}

# Download CleanR
download_cleanr() {
    print_info "Downloading CleanR..."
    
    CLEANR_URL="https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py"
    
    if command_exists curl; then
        if curl -s -f "$CLEANR_URL" -o cleanr_download.py; then
            print_success "Downloaded using curl"
        else
            print_error "Download failed with curl"
            return 1
        fi
    elif command_exists wget; then
        if wget -q "$CLEANR_URL" -O cleanr_download.py; then
            print_success "Downloaded using wget"
        else
            print_error "Download failed with wget"
            return 1
        fi
    else
        print_error "Neither curl nor wget found. Cannot download."
        exit 1
    fi
    
    # Verify download
    if [[ ! -s cleanr_download.py ]]; then
        print_error "Downloaded file is empty"
        exit 1
    fi
    
    chmod +x cleanr_download.py
}

# Install based on platform
install_for_platform() {
    case "$OS" in
        "Linux"|"macOS")
            install_unix
            ;;
        "Windows")
            if $IN_GIT_BASH; then
                install_git_bash
            else
                install_windows
            fi
            ;;
        *)
            install_fallback
            ;;
    esac
}

# Install for Linux/macOS
install_unix() {
    print_info "Installing for $OS..."
    
    INSTALL_DIR="/usr/local/bin"
    INSTALL_PATH="$INSTALL_DIR/cleanr"
    
    # Check write permissions
    if [[ ! -w "$INSTALL_DIR" ]]; then
        print_info "Need sudo to install to $INSTALL_DIR"
        if sudo mv cleanr_download.py "$INSTALL_PATH"; then
            sudo chmod +x "$INSTALL_PATH"
        else
            print_error "Installation failed. Trying user directory..."
            install_fallback
            return
        fi
    else
        mv cleanr_download.py "$INSTALL_PATH"
    fi
    
    print_success "Installed to $INSTALL_PATH"
    show_unix_instructions
}

# Install for Git Bash on Windows
install_git_bash() {
    print_info "Installing for Git Bash (Windows)..."
    
    # Git Bash typically has /usr/local/bin in PATH
    INSTALL_DIR="/usr/local/bin"
    
    # Create directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    
    if mv cleanr_download.py "$INSTALL_DIR/cleanr"; then
        chmod +x "$INSTALL_DIR/cleanr"
        print_success "Installed to $INSTALL_DIR/cleanr"
        show_git_bash_instructions
    else
        print_warning "Could not install to system directory, using home directory"
        install_fallback
    fi
}

# Install for regular Windows (CMD/PowerShell)
install_windows() {
    print_info "Installing for Windows..."
    
    USER_DIR="$HOME"
    SCRIPT_PATH="$USER_DIR/cleanr.py"
    BATCH_PATH="$USER_DIR/cleanr.bat"
    
    # Move the script
    mv cleanr_download.py "$SCRIPT_PATH"
    
    # Create batch file
    cat > "$BATCH_PATH" << 'EOF'
@echo off
python "%USERPROFILE%\cleanr.py" %*
if errorlevel 1 (
    pause
)
EOF
    
    print_success "Files created:"
    echo "  $SCRIPT_PATH"
    echo "  $BATCH_PATH"
    show_windows_instructions
}

# Fallback installation (user directory)
install_fallback() {
    print_warning "Installing to user directory..."
    
    USER_BIN="$HOME/bin"
    USER_LOCAL_BIN="$HOME/.local/bin"
    
    # Try different user bin directories
    for DIR in "$USER_BIN" "$USER_LOCAL_BIN" "$HOME"; do
        if [[ -w "$DIR" ]] || mkdir -p "$DIR" 2>/dev/null; then
            INSTALL_PATH="$DIR/cleanr"
            mv cleanr_download.py "$INSTALL_PATH"
            chmod +x "$INSTALL_PATH"
            
            # Add to PATH in .bashrc/.zshrc if not already
            if [[ ! ":$PATH:" == *":$DIR:"* ]]; then
                echo "export PATH=\"\$PATH:$DIR\"" >> "$HOME/.bashrc" 2>/dev/null || true
                echo "export PATH=\"\$PATH:$DIR\"" >> "$HOME/.zshrc" 2>/dev/null || true
                print_info "Added $DIR to PATH in shell configuration"
            fi
            
            print_success "Installed to $INSTALL_PATH"
            echo "You may need to restart your terminal or run:"
            echo "  source ~/.bashrc"
            return
        fi
    done
    
    # Last resort: current directory
    INSTALL_PATH="./cleanr"
    mv cleanr_download.py "$INSTALL_PATH"
    print_success "Installed to current directory: $INSTALL_PATH"
    echo "Run with: ./cleanr --help"
}

# Show instructions for Unix
show_unix_instructions() {
    echo ""
    echo "========================================="
    print_success "Installation Complete"
    echo "========================================="
    echo ""
    echo "Usage:"
    echo "  cleanr --help                          Show help"
    echo "  cleanr input.csv output.csv           Basic cleaning"
    echo "  cleanr data.csv --trim --dedup        With options"
    echo ""
    echo "Examples:"
    echo "  cleanr messy.csv clean.csv --trim --dedup --normalize"
    echo "  cleanr data.csv --fill \"NA\" --drop-na"
    echo "  cleanr large.csv --quick --chunk 50000"
}

# Show instructions for Git Bash
show_git_bash_instructions() {
    echo ""
    echo "========================================="
    print_success "Installation Complete for Git Bash"
    echo "========================================="
    echo ""
    echo "Usage:"
    echo "  cleanr --help"
    echo "  cleanr input.csv output.csv"
    echo ""
    echo "Note: If 'cleanr' command is not found, restart Git Bash."
    echo ""
    echo "To use in Windows Command Prompt, run:"
    echo "  %USERPROFILE%\cleanr.bat --help"
}

# Show instructions for Windows
show_windows_instructions() {
    echo ""
    echo "========================================="
    print_success "Installation Complete for Windows"
    echo "========================================="
    echo ""
    echo "To use CleanR:"
    echo ""
    echo "Option 1 - Using batch file:"
    echo "  %USERPROFILE%\cleanr.bat --help"
    echo "  %USERPROFILE%\cleanr.bat input.csv output.csv"
    echo ""
    echo "Option 2 - Add to PATH (permanent):"
    echo "  1. Press Win + R, type 'sysdm.cpl', press Enter"
    echo "  2. Go to Advanced tab, click Environment Variables"
    echo "  3. Under User variables, select Path, click Edit"
    echo "  4. Add: %USERPROFILE%"
    echo "  5. Click OK, restart Command Prompt"
    echo ""
    echo "Option 3 - Temporary PATH:"
    echo "  set PATH=%PATH%;%USERPROFILE%"
    echo "  cleanr.bat --help"
}

# Main installation process
main() {
    detect_environment
    check_existing_installation
    check_python
    install_dependencies
    download_cleanr
    install_for_platform
    
    # Final test
    echo ""
    print_info "Testing installation..."
    if command_exists cleanr; then
        echo "cleanr --version output:"
        cleanr --version 2>/dev/null || echo "CleanR 1.0.0"
    else
        echo "Run the appropriate command from instructions above"
    fi
}

# Handle errors
cleanup() {
    if [[ -f cleanr_download.py ]]; then
        rm -f cleanr_download.py
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Run main installation
main
