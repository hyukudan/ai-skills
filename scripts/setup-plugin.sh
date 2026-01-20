#!/bin/bash
# Quick setup: just link the Claude Code plugin
# Run: ./scripts/setup-plugin.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$HOME/.claude/plugins/aiskills"

echo "Setting up Claude Code plugin..."

mkdir -p "$HOME/.claude/plugins"

# Remove existing
[ -L "$PLUGIN_DIR" ] && rm "$PLUGIN_DIR"
[ -d "$PLUGIN_DIR" ] && mv "$PLUGIN_DIR" "${PLUGIN_DIR}.bak"

# Create symlink
ln -s "$REPO_DIR/plugin" "$PLUGIN_DIR"

echo "✓ Plugin linked: $PLUGIN_DIR"
echo ""
echo "Now install skills with:"
echo "  aiskills install $REPO_DIR/examples/skills/ --global --yes"
echo ""
echo "Restart Claude Code to use /skills, /skill, /skill-search"
