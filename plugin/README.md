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

## MCP Tools

Once connected, Claude Code has access to these tools:

| Tool | Description |
|------|-------------|
| `search_skills` | Search for skills using semantic + text hybrid search |
| `use_skill` | Load and render a skill's full content |
| `browse_skills` | Browse skills with lightweight metadata (tokens-efficient) |
| `list_skills` | List all installed skills |

Claude will automatically use these tools when you ask questions like:
- "How do I debug a Python memory leak?"
- "Show me skills about API design"
- "What testing strategies should I use?"

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
