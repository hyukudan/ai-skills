#!/bin/bash
# =============================================================================
# AI Skills - Universal Setup Script
# =============================================================================
# Sets up AI Skills for multiple CLI tools:
# - Claude Code (Anthropic)
# - Gemini CLI (Google)
# - Codex CLI (OpenAI)
#
# Usage: ./scripts/setup.sh [--claude] [--gemini] [--codex] [--all]
#        ./scripts/setup.sh              # Interactive mode
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_DIR/.venv"
WRAPPER_SCRIPT="$REPO_DIR/plugin/aiskills-wrapper.sh"

# CLI detection results
CLAUDE_INSTALLED=false
GEMINI_INSTALLED=false
CODEX_INSTALLED=false

# User selections
SETUP_CLAUDE=false
SETUP_GEMINI=false
SETUP_CODEX=false

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  AI Skills - Universal Setup"
    echo "=============================================="
    echo -e "${NC}"
}

detect_clis() {
    echo -e "${CYAN}Detecting installed CLI tools...${NC}"
    echo ""

    # Claude Code
    if command -v claude &> /dev/null; then
        CLAUDE_INSTALLED=true
        echo -e "  ${GREEN}✓${NC} Claude Code    ${GREEN}(installed)${NC}"
    else
        echo -e "  ${YELLOW}○${NC} Claude Code    ${YELLOW}(not found)${NC}"
    fi

    # Gemini CLI
    if command -v gemini &> /dev/null; then
        GEMINI_INSTALLED=true
        echo -e "  ${GREEN}✓${NC} Gemini CLI     ${GREEN}(installed)${NC}"
    else
        echo -e "  ${YELLOW}○${NC} Gemini CLI     ${YELLOW}(not found)${NC}"
    fi

    # Codex CLI
    if command -v codex &> /dev/null; then
        CODEX_INSTALLED=true
        echo -e "  ${GREEN}✓${NC} Codex CLI      ${GREEN}(installed)${NC}"
    else
        echo -e "  ${YELLOW}○${NC} Codex CLI      ${YELLOW}(not found)${NC}"
    fi

    echo ""
}

interactive_select() {
    # Pre-select installed CLIs by default
    $CLAUDE_INSTALLED && SETUP_CLAUDE=true
    $GEMINI_INSTALLED && SETUP_GEMINI=true
    $CODEX_INSTALLED && SETUP_CODEX=true

    local first_draw=true
    local menu_lines=8  # Number of lines in the menu (header + options + prompt)

    while true; do
        # Move cursor up and clear previous menu (except on first draw)
        if ! $first_draw; then
            # Move up menu_lines and clear each line
            for ((i=0; i<menu_lines; i++)); do
                echo -ne "\033[A\033[2K"
            done
        fi
        first_draw=false

        # Draw menu
        echo -e "${BOLD}Which CLI tools do you want to configure?${NC}"
        echo -e "${CYAN}(Press 1-3 to toggle, a=all, n=none, Enter=confirm, q=quit)${NC}"
        echo ""

        # Show checkbox for each CLI
        if $SETUP_CLAUDE; then
            echo -ne "  ${GREEN}[x]${NC} 1) Claude Code"
        else
            echo -ne "  [ ] 1) Claude Code"
        fi
        $CLAUDE_INSTALLED && echo -e "    ${GREEN}(installed)${NC}" || echo -e "    ${YELLOW}(not found)${NC}"

        if $SETUP_GEMINI; then
            echo -ne "  ${GREEN}[x]${NC} 2) Gemini CLI"
        else
            echo -ne "  [ ] 2) Gemini CLI"
        fi
        $GEMINI_INSTALLED && echo -e "     ${GREEN}(installed)${NC}" || echo -e "     ${YELLOW}(not found)${NC}"

        if $SETUP_CODEX; then
            echo -ne "  ${GREEN}[x]${NC} 3) Codex CLI"
        else
            echo -ne "  [ ] 3) Codex CLI"
        fi
        $CODEX_INSTALLED && echo -e "      ${GREEN}(installed)${NC}" || echo -e "      ${YELLOW}(not found)${NC}"

        echo ""
        read -p "> " -n1 choice

        case $choice in
            1) $SETUP_CLAUDE && SETUP_CLAUDE=false || SETUP_CLAUDE=true ;;
            2) $SETUP_GEMINI && SETUP_GEMINI=false || SETUP_GEMINI=true ;;
            3) $SETUP_CODEX && SETUP_CODEX=false || SETUP_CODEX=true ;;
            a|A)
                SETUP_CLAUDE=true
                SETUP_GEMINI=true
                SETUP_CODEX=true
                ;;
            n|N)
                SETUP_CLAUDE=false
                SETUP_GEMINI=false
                SETUP_CODEX=false
                ;;
            q|Q) echo ""; echo "Setup cancelled."; exit 0 ;;
            "") echo ""; break ;;  # Enter confirms
            *) ;;  # Ignore other keys
        esac
    done
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --claude) SETUP_CLAUDE=true; shift ;;
            --gemini) SETUP_GEMINI=true; shift ;;
            --codex) SETUP_CODEX=true; shift ;;
            --all)
                SETUP_CLAUDE=true
                SETUP_GEMINI=true
                SETUP_CODEX=true
                shift
                ;;
            --help|-h)
                echo "Usage: ./setup.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --claude    Configure Claude Code"
                echo "  --gemini    Configure Gemini CLI"
                echo "  --codex     Configure Codex CLI"
                echo "  --all       Configure all CLIs"
                echo "  --help      Show this help"
                echo ""
                echo "Without options, runs in interactive mode."
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
}

# =============================================================================
# Setup Functions
# =============================================================================

setup_python() {
    echo -e "${YELLOW}[1/5]${NC} Checking Python..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"
    else
        echo -e "  ${RED}✗${NC} Python 3 not found. Please install Python 3.10+"
        exit 1
    fi
}

setup_venv() {
    echo -e "${YELLOW}[2/5]${NC} Setting up virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        echo "  Using existing venv: $VENV_DIR"
    else
        echo "  Creating venv: $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"
    echo -e "  ${GREEN}✓${NC} Virtual environment activated"
}

install_package() {
    echo -e "${YELLOW}[3/5]${NC} Installing aiskills package..."

    pip install --quiet --upgrade pip
    pip install --quiet -e "$REPO_DIR[all]"

    echo -e "  ${GREEN}✓${NC} aiskills installed"
}

install_skills() {
    echo -e "${YELLOW}[4/5]${NC} Installing skills library..."

    aiskills install "$REPO_DIR/examples/skills/" --global --yes 2>/dev/null | tail -5

    SKILL_COUNT=$(aiskills list 2>/dev/null | grep -c "│" || echo "0")
    echo -e "  ${GREEN}✓${NC} $SKILL_COUNT skills installed"

    # Build search index
    aiskills search-index index 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Search index built"
}

# -----------------------------------------------------------------------------
# Claude Code Configuration
# -----------------------------------------------------------------------------
setup_claude() {
    echo -e "\n${CYAN}Configuring Claude Code...${NC}"

    if $CLAUDE_INSTALLED; then
        # Remove existing MCP server if present
        claude mcp remove aiskills 2>/dev/null || true

        # Add MCP server using wrapper script
        claude mcp add aiskills -- "$WRAPPER_SCRIPT" mcp serve
        echo -e "  ${GREEN}✓${NC} Claude Code MCP server configured"
    else
        echo -e "  ${YELLOW}!${NC} Claude Code not installed"
        echo "  After installing, run:"
        echo "  ${CYAN}claude mcp add aiskills -- $WRAPPER_SCRIPT mcp serve${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Gemini CLI Configuration
# -----------------------------------------------------------------------------
setup_gemini() {
    echo -e "\n${CYAN}Configuring Gemini CLI...${NC}"

    GEMINI_CONFIG_DIR="$HOME/.gemini"
    GEMINI_SETTINGS="$GEMINI_CONFIG_DIR/settings.json"

    # Create config directory if needed
    mkdir -p "$GEMINI_CONFIG_DIR"

    # Read existing config or create empty object
    if [ -f "$GEMINI_SETTINGS" ]; then
        EXISTING_CONFIG=$(cat "$GEMINI_SETTINGS")
    else
        EXISTING_CONFIG="{}"
    fi

    # Create the MCP server entry using Python (more reliable JSON handling)
    python3 << PYTHON_EOF
import json
import sys

config_path = "$GEMINI_SETTINGS"
wrapper_script = "$WRAPPER_SCRIPT"

# Load existing config
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add aiskills server
config['mcpServers']['aiskills'] = {
    'command': wrapper_script,
    'args': ['mcp', 'serve']
}

# Write updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("  ✓ Gemini CLI configured: " + config_path)
PYTHON_EOF

    if $GEMINI_INSTALLED; then
        echo -e "  ${GREEN}✓${NC} Gemini CLI MCP server configured"
    else
        echo -e "  ${YELLOW}!${NC} Gemini CLI not installed, but config created"
        echo "  Install Gemini CLI: ${CYAN}npm install -g @anthropic-ai/gemini-cli${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Codex CLI Configuration
# -----------------------------------------------------------------------------
setup_codex() {
    echo -e "\n${CYAN}Configuring Codex CLI...${NC}"

    CODEX_CONFIG_DIR="$HOME/.codex"
    CODEX_CONFIG="$CODEX_CONFIG_DIR/config.json"

    # Create config directory if needed
    mkdir -p "$CODEX_CONFIG_DIR"

    # Create the MCP server entry using Python
    python3 << PYTHON_EOF
import json

config_path = "$CODEX_CONFIG"
wrapper_script = "$WRAPPER_SCRIPT"

# Load existing config
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add aiskills server
config['mcpServers']['aiskills'] = {
    'command': wrapper_script,
    'args': ['mcp', 'serve']
}

# Write updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("  ✓ Codex CLI configured: " + config_path)
PYTHON_EOF

    if $CODEX_INSTALLED; then
        echo -e "  ${GREEN}✓${NC} Codex CLI MCP server configured"
    else
        echo -e "  ${YELLOW}!${NC} Codex CLI not installed, but config created"
        echo "  Install Codex CLI: ${CYAN}npm install -g @openai/codex${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Create Activation Script
# -----------------------------------------------------------------------------
create_activation_script() {
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
}

# -----------------------------------------------------------------------------
# Print Summary
# -----------------------------------------------------------------------------
print_summary() {
    echo ""
    echo -e "${GREEN}=============================================="
    echo "  Setup Complete!"
    echo "==============================================${NC}"
    echo ""

    echo -e "${BOLD}Configured CLIs:${NC}"
    $SETUP_CLAUDE && echo -e "  ${GREEN}✓${NC} Claude Code"
    $SETUP_GEMINI && echo -e "  ${GREEN}✓${NC} Gemini CLI"
    $SETUP_CODEX && echo -e "  ${GREEN}✓${NC} Codex CLI"
    echo ""

    echo -e "${BOLD}To use in terminal:${NC}"
    echo "  source $REPO_DIR/activate-aiskills.sh"
    echo "  aiskills use \"optimize my landing page\""
    echo ""

    if $SETUP_CLAUDE; then
        echo -e "${BOLD}In Claude Code:${NC}"
        echo "  /mcp                              - Verify connection"
        echo "  \"best practices for API design?\"  - Get guidance"
        echo ""
    fi

    if $SETUP_GEMINI; then
        echo -e "${BOLD}In Gemini CLI:${NC}"
        echo "  gemini mcp list                   - Verify connection"
        echo "  \"what skills do you have?\"        - List skills (auto-calls MCP)"
        echo "  \"help me debug python\"            - Get guidance (auto-calls MCP)"
        echo ""
    fi

    if $SETUP_CODEX; then
        echo -e "${BOLD}In Codex CLI:${NC}"
        echo "  codex mcp list                    - Verify connection"
        echo "  \"what testing skills are there?\"  - Search skills (auto-calls MCP)"
        echo "  \"help me write unit tests\"        - Get guidance (auto-calls MCP)"
        echo ""
    fi

    echo -e "${YELLOW}⚠  Restart your CLI tools to load the MCP server${NC}"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    print_header

    # Parse command line arguments
    if [ $# -gt 0 ]; then
        parse_args "$@"
    else
        # Interactive mode
        detect_clis
        interactive_select
    fi

    # Check if any CLI was selected
    if ! $SETUP_CLAUDE && ! $SETUP_GEMINI && ! $SETUP_CODEX; then
        echo -e "${YELLOW}No CLIs selected. Exiting.${NC}"
        exit 0
    fi

    echo ""
    echo -e "${BOLD}Selected:${NC}"
    $SETUP_CLAUDE && echo "  - Claude Code"
    $SETUP_GEMINI && echo "  - Gemini CLI"
    $SETUP_CODEX && echo "  - Codex CLI"
    echo ""

    # Core setup (always needed)
    setup_python
    setup_venv
    install_package
    install_skills

    # Configure selected CLIs
    echo -e "${YELLOW}[5/5]${NC} Configuring CLI tools..."

    $SETUP_CLAUDE && setup_claude
    $SETUP_GEMINI && setup_gemini
    $SETUP_CODEX && setup_codex

    create_activation_script
    print_summary
}

main "$@"
