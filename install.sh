#!/bin/bash
# install.sh - One-command CleanR installation

set -e

echo "Installing CleanR CSV Cleaner"
echo "================================="

# Create installation directory
INSTALL_DIR="$HOME/.cleanr"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "Installation directory: $INSTALL_DIR"

# Download or create main files
echo "Creating CleanR files..."

# Create cleanr executable
cat > cleanr << 'EOF'
#!/usr/bin/env bash
# [PASTE THE ENTIRE cleanr SCRIPT FROM SECTION 1 HERE]
EOF

# Create cleanr.py
cat > cleanr.py << 'EOF'
#!/usr/bin/env python3
# [PASTE THE ENTIRE cleanr.py SCRIPT FROM SECTION 2 HERE]
EOF

# Create profiles directory
mkdir -p profiles

# Create sample profiles
cat > profiles/sales.yaml << 'EOF'
# [PASTE sales.yaml FROM SECTION 3 HERE]
EOF

cat > profiles/personal.yaml << 'EOF'
# [PASTE personal.yaml FROM SECTION 3 HERE]
EOF

cat > profiles/ecommerce.yaml << 'EOF'
# [PASTE ecommerce.yaml FROM SECTION 3 HERE]
EOF

# Create config file
cat > .cleanr-config.yaml << 'EOF'
# [PASTE .cleanr-config.yaml FROM SECTION 4 HERE]
EOF

# Make executable
chmod +x cleanr cleanr.py

# Add to PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> ~/.bashrc
    echo "Added CleanR to PATH in ~/.bashrc"
fi

# Create alias for convenience
echo "alias cleanr='$INSTALL_DIR/cleanr'" >> ~/.bashrc

echo ""
echo "Installation complete!"
echo ""
echo "Quick start:"
echo "  1. Restart Git Bash or run: source ~/.bashrc"
echo "  2. Test with: cleanr --help"
echo "  3. Create your own profile: cleanr --create-profile mydata"
echo ""
echo "Usage examples:"
echo "  cleanr messy.csv --trim --dedup"
echo "  cleanr sales.csv --profile sales --stats"
echo "  cleanr large.csv --quick --chunk 50000"
echo ""
echo "Profiles installed: sales, personal, ecommerce"
echo "Edit profiles in: $INSTALL_DIR/profiles/"
