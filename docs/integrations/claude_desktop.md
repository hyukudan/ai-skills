# Claude Desktop Integration

This guide details how to set up **Ai Skills** as a Model Context Protocol (MCP) server for Claude Desktop. This integration allows Claude to search, read, and use your local skills directly within the chat interface.

## Prerequisites

-   [Claude Desktop](https://claude.ai/download) installed.
-   `aiskills` installed (`pip install aiskills[all]`).
-   (Optional) `uv` installed for faster, managed execution (recommended).

## Configuration

You need to edit the `claude_desktop_config.json` file. The location depends on your operating system:

-   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
-   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### Method 1: Using `uv` (Recommended)

This method ensures you run `aiskills` in an isolated environment without polluting your global Python setup.

```json
{
  "mcpServers": {
    "aiskills": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "aiskills",
        "mcp",
        "serve"
      ]
    }
  }
}
```

### Method 2: Direct Python Execution

If you have `aiskills` installed in your global Python environment or a specific virtual environment.

```json
{
  "mcpServers": {
    "aiskills": {
      "command": "/path/to/your/python",
      "args": [
        "-m",
        "aiskills",
        "mcp",
        "serve"
      ]
    }
  }
}
```
*Note: Replace `/path/to/your/python` with the output of `which python` (macOS/Linux) or `where python` (Windows).*

### Customizing the Skills Directory

By default, `aiskills` looks for skills in `~/.aiskills` or the current directory. To specify a custom location, add the `AISKILLS_HOME` environment variable:

```json
{
  "mcpServers": {
    "aiskills": {
      "command": "uv",
      "args": ["tool", "run", "aiskills", "mcp", "serve"],
      "env": {
        "AISKILLS_HOME": "/absolute/path/to/my/skills"
      }
    }
  }
}
```

## Verification

1.  Restart Claude Desktop completely.
2.  Look for the 🔌 icon (Project/Local integrations) in the Claude interface.
3.  You should see "aiskills" listed.
4.  Try asking Claude: *"Search for skills about python debugging"* or *"List available skills"*.

## Troubleshooting

### Server connection failed
-   Check the Claude Desktop logs:
    -   **macOS:** `~/Library/Logs/Claude/mcp-server-aiskills.log`
    -   **Windows:** `%APPDATA%\Claude\logs\mcp-server-aiskills.log`
-   Ensure the command specified in the config is executable and in your PATH.

### Skills not found
-   Verify the path set in `AISKILLS_HOME`.
-   Run `aiskills list` in your terminal to verify skills are detected independently of Claude.
