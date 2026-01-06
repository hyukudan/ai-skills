# aiskills Plugin for Claude Code

This plugin integrates the aiskills system with Claude Code, providing AI skills management through slash commands and MCP tools.

## Installation

1. Install aiskills:
```bash
pip install aiskills[all]
```

2. Copy or symlink this plugin directory to your Claude Code plugins:
```bash
# macOS/Linux
ln -s /path/to/aiskills/plugin ~/.claude/plugins/aiskills

# Or copy
cp -r /path/to/aiskills/plugin ~/.claude/plugins/aiskills
```

3. Restart Claude Code to load the plugin.

## Commands

### `/skill <name>`
Read a specific skill by name. Displays the skill's content and applies its guidance to the current task.

```
/skill python-debugging
/skill api-testing
```

### `/skills`
List all available skills installed in the system.

```
/skills
```

### `/skill-search <query>`
Search for skills using semantic similarity or text matching.

```
/skill-search "debug python errors"
/skill-search "API testing with pytest"
```

## MCP Tools

The plugin registers an MCP server that provides these tools:

- `skill_search` - Search for skills semantically
- `skill_read` - Read skill content with variable rendering
- `skill_list` - List all installed skills
- `skill_suggest` - Get skill suggestions for current context

## Configuration

The MCP server is configured in `plugin.json`. To use custom options, modify the server configuration:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "aiskills",
        "command": "aiskills",
        "args": ["mcp", "serve"],
        "env": {
          "AISKILLS_HOME": "/custom/path"
        }
      }
    ]
  }
}
```

## Requirements

- Python 3.10+
- aiskills package installed
- Claude Code with plugin support
