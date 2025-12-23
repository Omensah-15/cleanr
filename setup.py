#!/usr/bin/env python3
"""
CleanR Universal Installer
Works on Windows, Mac, Linux, Git Bash, WSL, CMD, PowerShell
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from urllib.request import urlopen

def print_color(text, color_code):
    """Print colored text if terminal supports it"""
    if sys.platform != "win32" or "ANSICON" in os.environ:
        print(f"\033[{color_code}m{text}\033[0m")
    else:
        print(text)

def success(msg):
    print_color(f"✓ {msg}", "32")

def info(msg):
    print_color(f"ℹ {msg}", "34")

def warning(msg):
    print_color(f"⚠ {msg}", "33")

def error(msg):
    print_color(f"✗ {msg}", "31")

def get_install_path():
    """Get the best installation path for the current OS"""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        # Windows paths
        paths = [
            home / "AppData" / "Local" / "Programs" / "CleanR",
            home / "CleanR",
            home / ".cleanr"
        ]
    else:
        # Unix-like paths
        paths = [
            home / ".local" / "bin",
            home / "bin",
            "/usr/local/bin"
        ]
    
    for path in paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
            if os.access(path, os.W_OK):
                return path / "cleanr"
        except:
            continue
    
    # Fallback to current directory
    return Path.cwd() / "cleanr"

def download_file(url, dest):
    """Download a file from URL"""
    try:
        info(f"Downloading {url}")
        response = urlopen(url)
        with open(dest, 'wb') as f:
            f.write(response.read())
        return True
    except Exception as e:
        error(f"Download failed: {e}")
        return False

def install_cleanr():
    """Main installation function"""
    print("\n" + "="*50)
    print("CleanR Professional CSV Cleaner - Installer")
    print("="*50)
    
    # Check Python
    info(f"Python {platform.python_version()} detected")
    
    # Install dependencies
    info("Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pandas", "pyyaml", "numpy", "--quiet"
        ], check=True)
        success("Dependencies installed")
    except subprocess.CalledProcessError:
        warning("Some dependencies may not have installed correctly")
    
    # Download cleanr.py
    install_path = get_install_path()
    info(f"Installing to: {install_path}")
    
    cleanr_url = "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py"
    if not download_file(cleanr_url, install_path):
        error("Installation failed")
        return False
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(install_path, 0o755)
    
    # Create launcher for Windows
    if platform.system() == "Windows":
        # Create batch file
        batch_path = install_path.parent / "cleanr.bat"
        with open(batch_path, 'w') as f:
            f.write(f'@"{sys.executable}" "{install_path}" %*\n')
        
        # Create PowerShell alias
        ps_path = install_path.parent / "cleanr.ps1"
        with open(ps_path, 'w') as f:
            f.write(f'& "{sys.executable}" "{install_path}" @args\n')
    
    # Add to PATH
    add_to_path(install_path.parent)
    
    # Verify installation
    if verify_installation(install_path):
        success("CleanR installed successfully!")
        show_instructions(install_path)
        return True
    else:
        error("Installation verification failed")
        return False

def add_to_path(install_dir):
    """Try to add install directory to PATH"""
    try:
        # Convert to string for PATH
        install_dir_str = str(install_dir)
        
        # Get current PATH
        if platform.system() == "Windows":
            path_var = os.environ.get("PATH", "")
            if install_dir_str not in path_var:
                info(f"Add this directory to PATH: {install_dir}")
                info(f"Or run: {install_dir}\\cleanr.bat --help")
        else:
            # Unix-like systems
            shell_rc = os.path.expanduser("~/.bashrc")
            if os.path.exists(shell_rc):
                with open(shell_rc, 'a') as f:
                    f.write(f'\n# CleanR installer\nexport PATH="$PATH:{install_dir}"\n')
                info(f"Added to PATH in ~/.bashrc")
                info("Run: source ~/.bashrc")
    except:
        warning("Could not automatically update PATH")

def verify_installation(install_path):
    """Verify the installation works"""
    try:
        result = subprocess.run(
            [str(install_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            info(f"Version: {result.stdout.strip()}")
            return True
    except:
        pass
    
    # Try alternative method
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("cleanr", install_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'main'):
            return True
    except:
        pass
    
    return False

def show_instructions(install_path):
    """Show usage instructions"""
    print("\n" + "="*50)
    print("USAGE INSTRUCTIONS")
    print("="*50)
    
    print("\nTo use CleanR:")
    
    if platform.system() == "Windows":
        print(f"1. Command Prompt:   {install_path.parent}\\cleanr.bat --help")
        print(f"2. PowerShell:       {install_path.parent}\\cleanr.ps1 --help")
        print(f"3. Git Bash:         cleanr --help (after restart)")
    else:
        print(f"1. Terminal:         cleanr --help")
        print(f"2. Direct:           {install_path} --help")
    
    print("\nExamples:")
    print("  cleanr input.csv output.csv --trim --dedup")
    print("  cleanr data.csv --normalize --fill 'NA'")
    print("  cleanr large.csv --quick --chunk 100000")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    try:
        if install_cleanr():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Unexpected error: {e}")
        sys.exit(1)
