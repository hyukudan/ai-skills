#!/bin/bash
# Deprecated: Use setup.sh instead
# This script is kept for backwards compatibility

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Note: setup-claude.sh is deprecated. Using setup.sh --claude instead."
echo ""

exec "$SCRIPT_DIR/setup.sh" --claude "$@"
