#!/bin/bash
# =============================================================================
# AI Skills - Automatic Setup for Claude Code
# =============================================================================
# This script sets up everything automatically:
# 1. Creates a Python virtual environment
# 2. Installs aiskills with all dependencies
# 3. Installs all bundled skills (marketing, development, etc.)
# 4. Configures the Claude Code plugin
#
# Usage: ./scripts/setup-claude.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_DIR/.venv"
PLUGIN_DIR="$HOME/.claude/plugins/aiskills"

echo -e "${BLUE}"
echo "=============================================="
echo "  AI Skills - Automatic Setup for Claude Code"
echo "=============================================="
echo -e "${NC}"

# -----------------------------------------------------------------------------
# Step 1: Check Python
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6]${NC} Checking Python..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "  ${RED}✗${NC} Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 2: Create virtual environment
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/6]${NC} Setting up virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo "  Using existing venv: $VENV_DIR"
else
    echo "  Creating venv: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
echo -e "  ${GREEN}✓${NC} Virtual environment activated"

# -----------------------------------------------------------------------------
# Step 3: Install aiskills
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/6]${NC} Installing aiskills package..."

pip install --quiet --upgrade pip
pip install --quiet -e "$REPO_DIR[all]"

echo -e "  ${GREEN}✓${NC} aiskills installed"

# -----------------------------------------------------------------------------
# Step 4: Install bundled skills
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/6]${NC} Installing skills library..."

# Install all skills globally
aiskills install "$REPO_DIR/examples/skills/" --global --yes 2>/dev/null | tail -5

SKILL_COUNT=$(aiskills list 2>/dev/null | grep -c "│" || echo "0")
echo -e "  ${GREEN}✓${NC} $SKILL_COUNT skills installed to ~/.aiskills/skills/"

# -----------------------------------------------------------------------------
# Step 5: Build search index
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/6]${NC} Building search index..."

aiskills search-index index 2>/dev/null
echo -e "  ${GREEN}✓${NC} Semantic search index built"

# -----------------------------------------------------------------------------
# Step 6: Setup Claude Code plugin
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/6]${NC} Configuring Claude Code plugin..."

mkdir -p "$HOME/.claude/plugins"

# Remove existing symlink/directory
[ -L "$PLUGIN_DIR" ] && rm "$PLUGIN_DIR"
[ -d "$PLUGIN_DIR" ] && mv "$PLUGIN_DIR" "${PLUGIN_DIR}.bak.$(date +%s)"

# Create symlink
ln -s "$REPO_DIR/plugin" "$PLUGIN_DIR"

echo -e "  ${GREEN}✓${NC} Plugin linked: $PLUGIN_DIR"

# -----------------------------------------------------------------------------
# Create activation helper script
# -----------------------------------------------------------------------------
ACTIVATE_SCRIPT="$REPO_DIR/activate-aiskills.sh"
cat > "$ACTIVATE_SCRIPT" << 'ACTIVATE_EOF'
#!/bin/bash
# Quick activation script for aiskills
# Usage: source activate-aiskills.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
echo "aiskills activated. Try: aiskills --help"
ACTIVATE_EOF
chmod +x "$ACTIVATE_SCRIPT"

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}=============================================="
echo "  Setup Complete!"
echo "==============================================${NC}"
echo ""
echo "Skills installed:"
echo "  - Marketing: page-cro, copywriting, seo-audit, paid-ads..."
echo "  - Development: python-debugging, api-design, testing..."
echo ""
echo -e "${BLUE}To use in terminal:${NC}"
echo "  source $REPO_DIR/activate-aiskills.sh"
echo "  aiskills use \"optimize my landing page\""
echo ""
echo -e "${BLUE}In Claude Code (after restart):${NC}"
echo "  /skills              - List all skills"
echo "  /skill page-cro      - Read a specific skill"
echo "  /skill-search \"CRO\"  - Search skills"
echo ""
echo -e "${YELLOW}⚠  Restart Claude Code to load the plugin${NC}"
echo ""
