# aiskills: Universal AI Skills for Any LLM

![License](https://img.shields.io/badge/license-AGPL--3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Status](https://img.shields.io/badge/status-active-success)

**aiskills** is a local-first skills management system that serves **any large language model**—Claude, ChatGPT, Gemini, Ollama, or your custom setup. Skills are stored as markdown files with YAML frontmatter, indexed for semantic search, and exposed through CLI, REST API, or MCP protocol. Write once, use everywhere.

## Why aiskills matters

- **One skill library for every model** – Claude, ChatGPT, Gemini, and other assistants consume the same skills, so expertise you capture once appears automatically across all your AI workflows.

- **Semantic discovery** – Find relevant skills by meaning, not just keywords. Ask "how to debug async code" and get back your Python debugging skill even if it doesn't contain those exact words.

- **Composable knowledge** – Skills can extend and include other skills, support template variables, and declare dependencies with semantic versioning constraints.

- **Private, local-first runtime** – All data lives on disk. No cloud APIs required. Index with FastEmbed + ChromaDB, both running locally.

- **Universal integrations** – REST API works with any HTTP client. OpenAI-compatible function definitions for ChatGPT/GPTs. MCP protocol for Claude Desktop. Plugin for Claude Code.

## Getting started

1. **Install aiskills**

   ```bash
   pip install aiskills[all]
   ```

   Or install only what you need:
   ```bash
   pip install aiskills              # Core CLI
   pip install aiskills[search]      # + semantic search (FastEmbed + ChromaDB)
   pip install aiskills[mcp]         # + MCP server
   pip install aiskills[api]         # + REST API (FastAPI)
   ```

2. **Create your first skill**

   ```bash
   aiskills init my-skill
   ```

   This creates a `SKILL.md` file with YAML frontmatter:

   ```yaml
   ---
   name: my-skill
   description: Brief description of when to use this skill
   version: 1.0.0
   tags: [topic, category]
   ---

   # My Skill

   Instructions for the AI agent...
   ```

3. **Install skills from GitHub**

   ```bash
   aiskills install owner/repo                    # From GitHub
   aiskills install git@github.com:owner/repo    # Via SSH
   aiskills install /path/to/local/skill         # Local path
   ```

4. **Search and use skills**

   ```bash
   aiskills list                                  # List installed skills
   aiskills search "debugging python"            # Semantic search
   aiskills read python-debugging                # Read for agent consumption
   ```

5. **Index for semantic search**

   ```bash
   aiskills search-index index                   # Build search index
   aiskills search "async error handling"        # Now finds by meaning
   ```

## SKILL.md format

Skills are markdown files with YAML frontmatter supporting rich metadata:

```yaml
---
name: python-debugging
description: |
  Expert debugging techniques for Python applications.
  Covers pdb, logging, profiling, and error handling.
version: 2.1.0
tags: [python, debugging, profiling, errors]
category: development/debugging

# Context helps semantic search understand when to suggest this skill
context: |
  Use this skill when debugging Python applications,
  investigating errors, tracing execution flow,
  or optimizing performance bottlenecks.

# Dependencies with semantic versioning constraints
dependencies:
  - name: python-basics
    version: ">=1.0.0"
  - name: logging-patterns
    version: "^2.0.0"
    optional: true

# Composition: extend or include other skills
extends: base-debugging
includes:
  - profiling-techniques
  - error-handling-patterns

# Template variables with types and defaults
variables:
  language:
    type: string
    default: python
    enum: [python, javascript, rust, go]
  include_profiling:
    type: boolean
    default: true
  max_depth:
    type: integer
    default: 10
---

# Python Debugging Techniques

## Core Debugging with pdb

```python
import pdb; pdb.set_trace()  # Classic breakpoint
breakpoint()                  # Python 3.7+ built-in
```

{% if include_profiling %}
## Profiling Section

Use cProfile for performance analysis:
```python
import cProfile
cProfile.run('my_function()')
```
{% endif %}

## Language-Specific Notes

These techniques are optimized for {{ language }}.
```

### Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier |
| `description` | Yes | What the skill does (multiline supported) |
| `version` | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| `tags` | No | List of tags for filtering |
| `category` | No | Hierarchical category (e.g., `development/testing`) |
| `context` | No | Additional context for semantic search |
| `dependencies` | No | Required skills with version constraints |
| `extends` | No | Base skill to extend |
| `includes` | No | Skills to include inline |
| `variables` | No | Template variables with types and defaults |

### Template syntax

Skills use Jinja2 templates:

- `{{ variable }}` – Insert variable value
- `{% if condition %}...{% endif %}` – Conditional sections
- `{% for item in list %}...{% endfor %}` – Loops

## CLI reference

```
aiskills <command> [options]

Commands:
  init <path>           Create a new skill from template
  install <source>      Install skill from GitHub, git URL, or local path
  remove <name>         Remove an installed skill
  list                  List all installed skills
  read <name>           Read skill content (formatted for agents)
  search <query>        Search skills semantically
  validate <path>       Validate skill structure
  sync                  Generate AGENTS.md from installed skills

  search-index index    Build/rebuild search index
  search-index stats    Show index statistics

  mcp serve             Start MCP server (for Claude)
  mcp info              Show MCP server information

  api serve             Start REST API server
  api info              Show API endpoints
```

### Examples

```bash
# Install from various sources
aiskills install python-debugging              # From registry (future)
aiskills install owner/repo                    # GitHub shorthand
aiskills install owner/repo#v2.0.0             # Specific version/tag
aiskills install git@github.com:owner/repo     # Git SSH
aiskills install https://github.com/o/r.git   # Git HTTPS
aiskills install ./local/skill                 # Local directory
aiskills install ~/skills/my-skill             # Home directory

# Search with filters
aiskills search "API testing"                  # Semantic search
aiskills search "debug" --text                 # Text-only search
aiskills search "python" --tag testing         # Filter by tag
aiskills search "web" --category development   # Filter by category
aiskills search "error" --limit 5              # Limit results

# Read with variables
aiskills read template-skill                   # Use defaults
aiskills read template-skill -v lang=rust      # Override variable

# List with filters
aiskills list                                  # All skills
aiskills list --global                         # Global only
aiskills list --json                           # JSON output
```

## Storage locations

```
~/.aiskills/                    # Global storage
├── skills/                     # Globally installed skills
├── cache/                      # Downloaded skill cache
├── registry/                   # Search index
│   └── vectors/                # ChromaDB vector store
└── aiskills.lock               # Global lock file

./.aiskills/                    # Project storage (higher priority)
├── skills/                     # Project-specific skills
├── variables.yaml              # Project variable overrides
└── aiskills.lock               # Project lock file

./.claude/skills/               # Claude Code compatibility
./.agent/skills/                # Universal agent compatibility
```

Skills in project directories take priority over global skills with the same name.

## Integrations

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          aiskills                                │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────────────┐  │
│  │   CLI    │   │  MCP Server  │   │       REST API          │  │
│  │          │   │  (Claude)    │   │  (OpenAI-compatible)    │  │
│  └────┬─────┘   └──────┬───────┘   └───────────┬─────────────┘  │
│       │                │                       │                 │
│       └────────────────┴───────────────────────┘                 │
│                            │                                     │
│              ┌─────────────┴─────────────┐                       │
│              │       Core Engine         │                       │
│              │  • SkillManager           │                       │
│              │  • SkillRegistry          │                       │
│              │  • SkillResolver          │                       │
│              │  • SkillRenderer          │                       │
│              └─────────────┬─────────────┘                       │
│                            │                                     │
│              ┌─────────────┴─────────────┐                       │
│              │     Search Backend        │                       │
│              │  • FastEmbed (embeddings) │                       │
│              │  • ChromaDB (vectors)     │                       │
│              └───────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Clients                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │  Claude   │ │  Claude   │ │  ChatGPT  │ │    Any HTTP     │  │
│  │   Code    │ │  Desktop  │ │  / GPTs   │ │     Client      │  │
│  │ (Plugin)  │ │  (MCP)    │ │  (REST)   │ │  (REST/OpenAI)  │  │
│  └───────────┘ └───────────┘ └───────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### MCP Server (Claude Desktop)

Start the MCP server for Claude Desktop integration:

```bash
aiskills mcp serve
```

Configure in `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aiskills": {
      "command": "aiskills",
      "args": ["mcp", "serve"]
    }
  }
}
```

**Available MCP tools:**

| Tool | Description |
|------|-------------|
| `skill_search` | Search skills by semantic similarity or text |
| `skill_read` | Read skill content with variable rendering |
| `skill_list` | List all installed skills |
| `skill_suggest` | Suggest relevant skills for current context |

### REST API (ChatGPT, Gemini, etc.)

Start the REST API server:

```bash
aiskills api serve                    # Default: http://localhost:8420
aiskills api serve --port 3000        # Custom port
aiskills api serve --host 0.0.0.0     # Bind to all interfaces
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/skills` | List all skills |
| GET | `/skills/{name}` | Get skill by name |
| POST | `/skills/read` | Read with variables |
| POST | `/skills/search` | Search skills |
| POST | `/skills/suggest` | Get suggestions |
| GET | `/openai/tools` | OpenAI-format tool definitions |
| POST | `/openai/call` | Execute OpenAI function call |
| GET | `/docs` | Swagger documentation |

**Example usage:**

```bash
# List skills
curl http://localhost:8420/skills

# Search
curl -X POST http://localhost:8420/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query": "debugging python", "limit": 5}'

# Get OpenAI-compatible tools
curl http://localhost:8420/openai/tools

# Execute function call (OpenAI format)
curl -X POST http://localhost:8420/openai/call \
  -H "Content-Type: application/json" \
  -d '{"name": "skill_search", "arguments": {"query": "testing APIs"}}'
```

### Claude Code Plugin

Install the plugin:

```bash
ln -s /path/to/aiskills/plugin ~/.claude/plugins/aiskills
```

**Slash commands:**

| Command | Description |
|---------|-------------|
| `/skill <name>` | Read a skill by name |
| `/skills` | List available skills |
| `/skill-search <query>` | Search for skills |

### AGENTS.md Generation

Generate documentation for AI agents:

```bash
aiskills sync                         # Creates AGENTS.md
aiskills sync -o docs/AGENTS.md       # Custom output path
aiskills sync --no-global             # Project skills only
```

## Platform guides

| Platform | Integration | Guide |
|----------|-------------|-------|
| **Claude Code** | Plugin + MCP | [plugin/README.md](./plugin/README.md) |
| **Claude Desktop** | MCP Server | [#mcp-server](#mcp-server-claude-desktop) |
| **ChatGPT / Custom GPTs** | REST API | [docs/integrations/chatgpt.md](./docs/integrations/chatgpt.md) |
| **Google Gemini** | REST API | [docs/integrations/gemini.md](./docs/integrations/gemini.md) |
| **LangChain / AutoGen** | REST API | [docs/integrations/other-llms.md](./docs/integrations/other-llms.md) |
| **Ollama / Local** | REST API | [docs/integrations/other-llms.md](./docs/integrations/other-llms.md) |

## Semantic search

aiskills uses local embeddings for semantic search:

- **FastEmbed** – ONNX-based embeddings (BAAI/bge-small-en-v1.5)
- **ChromaDB** – Local vector store with SQLite backend

```bash
# Install search dependencies
pip install aiskills[search]

# Index your skills
aiskills search-index index

# Search semantically
aiskills search "how to handle async errors"

# View index stats
aiskills search-index stats
```

Search uses both the skill's description and `context` field for better relevance.

## Version constraints

Dependencies support npm-style version constraints:

| Constraint | Meaning |
|------------|---------|
| `1.0.0` | Exact version |
| `>=1.0.0` | Greater than or equal |
| `>1.0.0` | Greater than |
| `<=1.0.0` | Less than or equal |
| `<1.0.0` | Less than |
| `^1.2.3` | Compatible (>=1.2.3 <2.0.0) |
| `~1.2.3` | Approximately (>=1.2.3 <1.3.0) |
| `*` | Any version |

## Development

```bash
# Clone repository
git clone https://github.com/sergioc/aiskills.git
cd aiskills

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with all dependencies
pip install -e ".[all,dev]"

# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src
```

## Roadmap

- [ ] Public skill registry
- [ ] Skill versioning and updates
- [ ] Skill rating and reviews
- [ ] Team/organization support
- [ ] Skill analytics
- [ ] VS Code extension
- [ ] JetBrains plugin

## Credits

Inspired by [OpenSkills](https://github.com/numman-ali/openskills) and the broader movement toward sharable AI agent knowledge. Built to work seamlessly with [ai-mem](https://github.com/sergioc/ai-mem) for combined skills + memory workflows.

## License

AGPL-3.0
