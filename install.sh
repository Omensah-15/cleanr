#!/bin/bash

# CleanR Universal Installer - Works Everywhere
set -e

# Colors for clean output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Simple print functions
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to safely run commands with error handling
safe_run() {
    if "$@" > /tmp/cleanr_install.log 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main installation function
install_cleanr() {
    echo "=========================================="
    echo "CleanR Professional CSV Cleaner"
    echo "=========================================="
    
    # Detect environment
    detect_environment
    
    # Check Python
    check_python
    
    # Install dependencies
    install_dependencies
    
    # Download and install
    download_and_install
    
    # Verify installation
    verify_installation
    
    echo "=========================================="
    print_success "Installation Complete!"
    echo "=========================================="
}

# Detect OS and environment
detect_environment() {
    # Get OS type
    case "$(uname -s)" in
        Linux*)     OS="Linux" ;;
        Darwin*)    OS="macOS" ;;
        CYGWIN*)    OS="Windows" ;;
        MINGW*)     OS="Windows" ;;
        MSYS*)      OS="Windows" ;;
        *)          OS="Unknown" ;;
    esac
    
    # Check if in WSL
    if [[ -n "$WSL_DISTRO_NAME" ]] || grep -q microsoft /proc/version 2>/dev/null; then
        IS_WSL=true
    else
        IS_WSL=false
    fi
    
    # Check if in Git Bash
    if [[ -n "$MSYSTEM" ]] && [[ "$MSYSTEM" =~ MINGW ]]; then
        IN_GIT_BASH=true
    else
        IN_GIT_BASH=false
    fi
    
    print_info "Operating System: $OS"
    [[ "$IS_WSL" = true ]] && print_info "Running in WSL"
    [[ "$IN_GIT_BASH" = true ]] && print_info "Running in Git Bash"
}

# Check Python installation
check_python() {
    # Try python3 first, then python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON=python
    else
        print_error "Python not found"
        echo ""
        echo "Please install Python from: https://www.python.org/downloads/"
        echo "Make sure to check 'Add Python to PATH' during installation."
        exit 1
    fi
    
    # Verify Python can run
    if ! $PYTHON -c "import sys; print('Python', sys.version)" >/dev/null 2>&1; then
        print_error "Python is not working properly"
        exit 1
    fi
    
    print_success "Python found: $($PYTHON --version 2>&1)"
}

# Install dependencies
install_dependencies() {
    print_info "Checking dependencies..."
    
    # Get pip command
    if command -v pip3 >/dev/null 2>&1; then
        PIP=pip3
    elif command -v pip >/dev/null 2>&1; then
        PIP=pip
    else
        # Try to use python -m pip
        PIP="$PYTHON -m pip"
    fi
    
    # Install packages quietly
    for package in pandas pyyaml numpy; do
        if $PIP list | grep -q "$package"; then
            print_info "$package already installed"
        else
            print_info "Installing $package..."
            if ! $PIP install "$package" --quiet --disable-pip-version-check; then
                print_warning "Failed to install $package, trying with --user flag..."
                $PIP install "$package" --user --quiet --disable-pip-version-check || true
            fi
        fi
    done
    
    print_success "Dependencies verified"
}

# Download and install CleanR
download_and_install() {
    print_info "Downloading CleanR..."
    
    # Download the script
    DOWNLOAD_URL="https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py"
    
    if command -v curl >/dev/null 2>&1; then
        curl -sSL "$DOWNLOAD_URL" -o /tmp/cleanr_download.py
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$DOWNLOAD_URL" -O /tmp/cleanr_download.py
    else
        print_error "Neither curl nor wget found. Cannot download."
        exit 1
    fi
    
    # Verify download
    if [[ ! -s /tmp/cleanr_download.py ]]; then
        print_error "Download failed or file is empty"
        exit 1
    fi
    
    # Make executable
    chmod +x /tmp/cleanr_download.py
    
    # Determine install location
    determine_install_location
    
    # Install
    print_info "Installing to: $INSTALL_PATH"
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$INSTALL_PATH")"
    
    # Copy the file
    cp /tmp/cleanr_download.py "$INSTALL_PATH"
    
    # Make sure it's executable
    chmod +x "$INSTALL_PATH"
    
    # Clean up
    rm -f /tmp/cleanr_download.py
}

# Determine best install location
determine_install_location() {
    # Default to user's bin directory
    USER_BIN="$HOME/.local/bin"
    
    # Check various possible locations
    for dir in "$HOME/bin" "$USER_BIN" "/usr/local/bin" "$HOME/.bin"; do
        # Try to create directory if it doesn't exist
        if mkdir -p "$dir" 2>/dev/null && [[ -w "$dir" ]]; then
            INSTALL_PATH="$dir/cleanr"
            
            # Check if already in PATH
            if echo "$PATH" | tr ':' '\n' | grep -q "^$(dirname "$INSTALL_PATH")$"; then
                print_info "Found suitable directory in PATH: $dir"
                return
            fi
        fi
    done
    
    # Fallback to user's home directory
    INSTALL_PATH="$HOME/cleanr"
    print_warning "Installing to home directory. You may need to add it to PATH."
}

# Update PATH if needed
update_path() {
    local install_dir=$(dirname "$INSTALL_PATH")
    
    # Check if already in PATH
    if echo "$PATH" | tr ':' '\n' | grep -q "^$install_dir$"; then
        return 0
    fi
    
    # Try to add to PATH
    for rc_file in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.zshrc" "$HOME/.profile"; do
        if [[ -f "$rc_file" ]] || [[ -w "$(dirname "$rc_file")" ]]; then
            echo "# Added by CleanR installer" >> "$rc_file"
            echo "export PATH=\"\$PATH:$install_dir\"" >> "$rc_file"
            print_info "Added $install_dir to PATH in $rc_file"
            return 0
        fi
    done
    
    print_warning "Could not automatically add to PATH. Add this line to your shell config:"
    echo "  export PATH=\"\$PATH:$install_dir\""
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    # Try to run cleanr
    if "$INSTALL_PATH" --version >/dev/null 2>&1; then
        print_success "CleanR installed successfully!"
        echo ""
        echo "Location: $INSTALL_PATH"
        
        # Update PATH
        update_path
        
        # Show usage instructions
        show_instructions
    else
        print_error "Installation verification failed"
        echo "You can still try to run: $INSTALL_PATH --help"
    fi
}

# Show usage instructions
show_instructions() {
    echo ""
    echo "USAGE:"
    echo "  cleanr --help                          Show help"
    echo "  cleanr input.csv output.csv            Basic cleaning"
    echo "  cleanr data.csv --trim --dedup         With options"
    echo ""
    echo "EXAMPLES:"
    echo "  cleanr messy.csv clean.csv --trim --dedup --normalize"
    echo "  cleanr data.csv --fill \"NA\" --drop-na"
    echo "  cleanr large.csv --quick --chunk 50000"
    echo ""
    
    # Platform-specific notes
    case "$OS" in
        "Windows")
            if [[ "$IN_GIT_BASH" = true ]]; then
                echo "Note: If 'cleanr' command doesn't work immediately, restart Git Bash."
            else
                echo "For Windows CMD/PowerShell, run:"
                echo "  $INSTALL_PATH --help"
            fi
            ;;
        *)
            echo "If 'cleanr' command is not found, run:"
            echo "  source ~/.bashrc  # or restart your terminal"
            ;;
    esac
}

# Clean up on exit
cleanup() {
    rm -f /tmp/cleanr_download.py /tmp/cleanr_install.log 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Run installation
install_cleanr
