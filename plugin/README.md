# aiskills Plugin for Claude Code

This plugin integrates the aiskills system with Claude Code, providing AI skills management through MCP (Model Context Protocol).

## Installation

### 1. Install aiskills

```bash
pip install aiskills[all]

# Or from source
cd /path/to/ai-skills
pip install -e ".[all]"
```

### 2. Configure the MCP Server

Add the aiskills MCP server to Claude Code:

```bash
# Using the wrapper script (recommended - handles virtualenv activation)
claude mcp add aiskills -- /path/to/ai-skills/plugin/aiskills-wrapper.sh mcp serve

# Or directly if aiskills is in your PATH
claude mcp add aiskills -- aiskills mcp serve
```

### 3. Restart Claude Code

Exit Claude Code (`/exit` or Ctrl+D) and start it again. You should see the MCP server connected:

```bash
claude
# Check connection with:
/mcp
```

## Verifying the Connection

After restarting Claude Code, run `/mcp` to verify the server is connected:

```
/mcp
⎿  MCP servers: aiskills (connected)
```

If it shows "No MCP servers configured", check:
- The path to `aiskills-wrapper.sh` is correct
- The wrapper script is executable (`chmod +x plugin/aiskills-wrapper.sh`)
- aiskills is properly installed in the virtualenv

## Quick Test

Once connected, try these commands in Claude Code to verify everything works:

```
# List available skills
> list all skills

# Search for a topic
> search skills about testing

# Read a specific skill
> show me the api-design skill

# Get guidance (uses use_skill)
> what are best practices for API design?
```

## MCP Tools

| Tool | When Claude Uses It |
|------|---------------------|
| `use_skill` | When you ask for best practices, design patterns, or architectural guidance |
| `skill_search` | When you explicitly ask to search or find skills |
| `skill_read` | When you ask to show/read a specific skill by name |
| `skill_list` | When you ask "what skills are available" |
| `skill_suggest` | When you ask for skill recommendations |
| `skill_categories` | When you want to browse skills by category |

### When Skills Are Used (Token Optimization)

To avoid unnecessary API calls, Claude **only** uses skills when you:
- Explicitly ask for best practices or design guidance
- Ask about skills directly ("list skills", "search skills", "show skill X")
- Request architectural or strategic help

Claude will **not** use skills for:
- Simple code questions or syntax help
- Quick bug fixes
- General conversation

## Troubleshooting

### Server not connecting

1. Check the wrapper script exists and is executable:
   ```bash
   ls -la /path/to/ai-skills/plugin/aiskills-wrapper.sh
   ```

2. Test the wrapper script manually:
   ```bash
   /path/to/ai-skills/plugin/aiskills-wrapper.sh --version
   ```

3. Check MCP server configuration:
   ```bash
   claude mcp list
   ```

4. Remove and re-add the server:
   ```bash
   claude mcp remove aiskills
   claude mcp add aiskills -- /path/to/ai-skills/plugin/aiskills-wrapper.sh mcp serve
   ```

### Skills not found

Make sure skills are installed:
```bash
aiskills list
aiskills install examples/skills/ --global
```

## Configuration

The MCP server can be configured with environment variables:

```bash
claude mcp add -e AISKILLS_HOME=/custom/path aiskills -- aiskills mcp serve
```

| Variable | Description |
|----------|-------------|
| `AISKILLS_HOME` | Custom skills directory |
| `AISKILLS_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Requirements

- Python 3.10+
- aiskills package installed
- Claude Code v2.1.0+ with MCP support
