#!/bin/bash

# Product Insights AI — First-Time Setup Wizard
# This script configures your environment for using the analytics agent

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         PRODUCT INSIGHTS AI — SETUP WIZARD                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3.9 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Step 2: Install dependencies
echo ""
echo -e "${YELLOW}[2/5]${NC} Installing dependencies..."
python3 -m pip install -q pyyaml snowflake-connector-python 2>/dev/null || {
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    echo "Try: python3 -m pip install pyyaml snowflake-connector-python"
    exit 1
}
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 3: Create config directory
echo ""
echo -e "${YELLOW}[3/5]${NC} Setting up configuration directory..."
CONFIG_DIR="$HOME/.config/alteryx"
mkdir -p "$CONFIG_DIR"
echo -e "${GREEN}✓${NC} Config directory: $CONFIG_DIR"

# Step 4: Ask for Snowflake credentials
echo ""
echo -e "${YELLOW}[4/5]${NC} Snowflake Configuration"
echo ""
echo "Enter your Snowflake credentials (saved to ~/.config/alteryx/)"
echo ""

read -p "Snowflake Account Identifier (e.g., ALTERYX-ALTERYX_EDW): " SF_ACCOUNT
read -p "Snowflake User (e.g., AYX105566@ALTERYX.COM): " SF_USER
read -p "Snowflake Role (e.g., DHIRAJ_SAHU_ROLE): " SF_ROLE
read -p "Snowflake Warehouse (e.g., ANALYTICS_WH): " SF_WAREHOUSE

# Save credentials
cat > "$CONFIG_DIR/snowflake.env" << EOF
export SF_ACCOUNT="$SF_ACCOUNT"
export SF_USER="$SF_USER"
export SF_ROLE="$SF_ROLE"
export SF_WAREHOUSE="$SF_WAREHOUSE"
EOF

chmod 600 "$CONFIG_DIR/snowflake.env"
echo -e "${GREEN}✓${NC} Credentials saved (secure: 600 permissions)"

# Step 5: Test connection
echo ""
echo -e "${YELLOW}[5/5]${NC} Testing Snowflake connection..."

source "$CONFIG_DIR/snowflake.env"

TEST_RESULT=$(python3 << 'PYTHON_EOF'
import os
try:
    import snowflake.connector
    conn = snowflake.connector.connect(
        account=os.getenv('SF_ACCOUNT'),
        user=os.getenv('SF_USER'),
        authenticator='externalbrowser',
        role=os.getenv('SF_ROLE'),
        warehouse=os.getenv('SF_WAREHOUSE')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
    result = cursor.fetchone()
    conn.close()
    print(f"SUCCESS|{result[0]}|{result[1]}|{result[2]}")
except Exception as e:
    print(f"ERROR|{str(e)}")
PYTHON_EOF
)

if [[ $TEST_RESULT == ERROR* ]]; then
    echo -e "${RED}✗ Connection failed${NC}"
    echo "Error: $(echo $TEST_RESULT | cut -d'|' -f2-)"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check your account identifier and user"
    echo "  • Verify your Snowflake role has warehouse access"
    echo "  • Try running: snow connection test"
    exit 1
else
    USER=$(echo $TEST_RESULT | cut -d'|' -f2)
    ROLE=$(echo $TEST_RESULT | cut -d'|' -f3)
    WH=$(echo $TEST_RESULT | cut -d'|' -f4)
    echo -e "${GREEN}✓${NC} Connection successful"
    echo "  User: $USER"
    echo "  Role: $ROLE"
    echo "  Warehouse: $WH"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  SETUP COMPLETE ✓                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}You're ready to start!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the agent:"
echo "     ${YELLOW}python agent/cli/main.py${NC}"
echo ""
echo "  2. Try an example question:"
echo "     ${YELLOW}How many active users did we have last month?${NC}"
echo ""
echo "  3. Explore other products:"
echo "     ${YELLOW}What is our Copilot adoption rate?${NC}"
echo ""
echo "  4. For contributing metrics:"
echo "     See ${YELLOW}CONTRIBUTING.md${NC}"
echo ""
echo "Questions? Check:"
echo "  • ${YELLOW}README.md${NC} — Quick start guide"
echo "  • ${YELLOW}docs/FAQ.md${NC} — Common questions"
echo "  • ${YELLOW}docs/GOVERNANCE.md${NC} — Contribution process"
echo ""
echo "Happy analyzing! 🚀"
echo ""
