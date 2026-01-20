#!/bin/bash
# Wrapper for aiskills CLI that activates the virtual environment
# This allows Claude Code's MCP server to find the aiskills command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_DIR/.venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    exec aiskills "$@"
else
    echo "Error: Virtual environment not found at $VENV_DIR" >&2
    echo "Run: ./scripts/setup-claude.sh" >&2
    exit 1
fi
