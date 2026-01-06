"""Global constants for aiskills."""

from pathlib import Path

# File names
SKILL_FILE = "SKILL.md"
LOCK_FILE = "aiskills.lock"
CONFIG_FILE = "aiskills.yaml"
VARIABLES_FILE = "variables.yaml"

# Directory names
SKILLS_DIR = "skills"
CACHE_DIR = "cache"
REGISTRY_DIR = "registry"
REFERENCES_DIR = "references"
SCRIPTS_DIR = "scripts"
ASSETS_DIR = "assets"

# Search paths (in priority order)
PROJECT_DIRS = [
    ".aiskills",  # aiskills native (highest priority)
    ".claude",  # Claude Code compatibility
    ".agent",  # Universal agent compatibility
]

GLOBAL_BASE = Path.home() / ".aiskills"

# Frontmatter markers
FRONTMATTER_DELIMITER = "---"

# Limits
MAX_SKILL_SIZE_KB = 500  # Max SKILL.md size in KB
MAX_DESCRIPTION_LENGTH = 1000
MAX_CONTEXT_LENGTH = 2000

# Version
MIN_PYTHON_VERSION = "3.10"
