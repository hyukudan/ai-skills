"""MCP (Model Context Protocol) server for aiskills.

Exposes skills as MCP tools for use with Claude Desktop and other MCP clients.

Tools:
- skill_search: Search for skills semantically or by text
- skill_read: Read skill content with optional variable rendering
- skill_list: List all installed skills
- skill_suggest: Suggest relevant skills based on context
"""

from .server import create_server, main, run_server
from .tools import (
    TOOL_DEFINITIONS,
    SkillListInput,
    SkillReadInput,
    SkillSearchInput,
    SkillSuggestInput,
)

__all__ = [
    "create_server",
    "run_server",
    "main",
    "TOOL_DEFINITIONS",
    "SkillSearchInput",
    "SkillReadInput",
    "SkillListInput",
    "SkillSuggestInput",
]
