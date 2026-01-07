# Ai Skills

![Ai Skills Header](./docs/assets/ai_skills_header_vibrant.png)

<div align="center">

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://python.org)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](https://github.com/sergioc/ai-skills)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange?style=flat-square)](https://pypi.org/project/aiskills)


**Universal AI Knowledge for Everyone**
*Write skills once. Use them with Claude, ChatGPT, Gemini, and Ollama.*

[Quick Start](#-quick-start) • [Core Concepts](#-core-concepts) • [Integrations](#-integrations) • [Architecture](#-architecture) • [Documentation](#-documentation)

</div>

---

**Ai Skills** is a local-first skills management system that serves **any large language model**. It transforms static markdown files into dynamic, semantically searchable tools that your AI agents—whether local or cloud-based—can use to solve complex problems.

## 🚀 Quick Start

Get started in seconds.

### 1. Install
```bash
pip install aiskills[all]
```
*(Recommended: Use a virtual environment or `uv tool install aiskills`)*

### 2. Initialize
Create your first skill library:
```bash
aiskills init my-first-skill
```

### 3. Search
Find skills semantically:
```bash
aiskills search "how to debug python"
# Returns specific debugging skills based on semantic meaning
```

### 4. Use Skills Naturally
Invoke skills with natural language:
```bash
aiskills use "debug python memory leak"
# Finds and displays the best matching skill automatically
```

### 5. Serve (Optional)
Start the API/MCP server to connect with apps:
```bash
aiskills api serve
```

## 💡 Core Concepts

Ai Skills is built on three simple pillars:

1.  **Skills**: Standard Markdown files with YAML frontmatter. Readable by humans, parsable by machines.
2.  **Engine**: A Python core that handles hot-reloading, template rendering, and dependency resolution.
3.  **Interfaces**: Multiple ways to access your skills—CLI, REST API, or MCP (Model Context Protocol).

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph Interfaces
        CLI[CLI]
        API[REST API]
        MCP[MCP Server]
    end
    
    subgraph Core
        Router[SkillRouter]
        Registry[Registry]
        Manager[Manager]
    end
    
    subgraph Storage
        Skills[(Skills)]
        Index[(Search Index)]
    end
    
    CLI --> Router
    API --> Router
    MCP --> Router
    
    Router --> Registry
    Router --> Manager
    Registry --> Index
    Manager --> Skills
```

### Skill Router

The **Skill Router** is the intelligent core that powers natural language skill discovery. All interfaces (CLI, REST API, MCP) use the same router, ensuring consistent behavior everywhere.

```python
from aiskills.core.router import get_router

router = get_router()
result = router.use("debug python memory leak")

print(result.skill_name)   # → "python-debugging"
print(result.score)        # → 0.89 (similarity score)
print(result.content)      # → Rendered skill content
```

**Features:**
- 🔍 **Semantic Search** with automatic fallback to text search
- 📝 **Template Variables** for dynamic skill content
- 🔄 **Multiple Results** with `limit` parameter
- ⚡ **Lazy Loading** for fast startup

### Access Methods

| Method | Command / Endpoint | Example |
|--------|-------------------|---------|
| **CLI** | `aiskills use` | `aiskills use "write unit tests"` |
| **REST API** | `POST /skills/use` | `{"context": "optimize SQL"}` |
| **MCP Tool** | `use_skill` | Called by Claude/agents |
| **Python** | `router.use()` | Direct SDK usage |

## 🔌 Integrations

Connect your skills to your favorite tools.

| Platform | Integration Method | Status | Guide |
| :--- | :--- | :--- | :--- |
| **Claude Desktop** | MCP Server | ✅ Ready | [**Setup Guide**](docs/integrations/claude_desktop.md) |
| **Google Gemini** | Function Calling | ✅ Ready | [**Gemini Guide**](docs/integrations/gemini.md) |
| **Ollama / Local** | Tool Calling / CLI | ✅ Ready | [**Ollama Guide**](docs/integrations/ollama.md) |
| **ChatGPT** | Custom GPT / Actions | ✅ Ready | [ChatGPT Guide](docs/integrations/chatgpt.md) |
| **Claude Code** | Plugin | ✅ Ready | [Plugin Guide](plugin/README.md) |
| **Custom Agents** | Python SDK | ✅ Ready | [SDK Docs](docs/sdk.md) |

## 📖 Skill Format

Skills are simple markdown files with power-packed frontmatter.

```markdown
---
name: python-expert
description: Advanced Python debugging and optimization techniques.
tags: [python, coding, debug]
dependencies:
  - name: coding-basics
    version: ">=1.0.0"
---

# Python Expert Guide

## Memory Management
Use `tracemalloc` to identify leaks...
```

## 📚 Documentation

### Progressive Disclosure

Ai Skills implements a **3-phase progressive disclosure** system that optimizes context window usage:

```
Phase 1: BROWSE    →    Phase 2: LOAD    →    Phase 3: USE
(metadata only)         (full content)        (extra resources)
```

- **Browse** (`aiskills browse`): Returns lightweight metadata (name, description, `tokens_est`) without loading content. Perfect for discovering relevant skills before committing tokens.
- **Load** (`aiskills use`): Fetches the full rendered skill content.
- **Use** (on-demand): Load additional resources (templates, references, scripts) only when needed.

📖 [Full Guide](docs/progressive-disclosure.md)

### Declarative Scoping

Go beyond semantic search with **explicit matching rules** that reduce false positives:

```yaml
scope:
  paths: ["src/api/**", "migrations/**"]    # Only match when touching these files
  languages: [python, sql]                   # Only match for these languages
  triggers: [migrate, alembic, revision]     # Hard keywords that boost this skill

priority: 75              # 0-100, higher = more preferred
precedence: repository    # organization > repository > project > user > local
```

The router combines semantic similarity with scope matching for accurate skill selection.

📖 [Full Guide](docs/scoping.md)

### Local Overrides

Customize shared skills without modifying the original using `SKILL.local.md`:

```
my-skill/
├── SKILL.md           # Shared/versioned (in git)
└── SKILL.local.md     # Private overrides (gitignored)
```

Local overrides can:
- **Override** scalars (priority, precedence)
- **Extend** lists (tags, includes)
- **Deep merge** objects (scope, security, variables)
- **Append** content (add team-specific sections)

📖 [Full Guide](docs/local-overrides.md)

### Security & Sandboxing

Control what resources skills can access with the `security` policy:

```yaml
security:
  allowed_resources: [references, templates]  # What can be loaded
  allow_execution: false                      # Can scripts run?
  sandbox_level: standard                     # strict | standard | permissive
  allowlist: [deploy.sh, validate.py]         # Specific allowed scripts
```

Resources are tagged with `requires_execution` and `allowed` flags for agent decision-making.

📖 [Full Guide](docs/security.md)

### Skill Composition

Reuse content without duplication using `@include`:

```markdown
# My Guide

## Python Section
@include python-debugging

## Common Patterns
@include snippets/patterns.md
```

Features:
- Include other skills: `@include skill:name`
- Include snippets: `@include path/to/file.md`
- **Depth limit** (5) prevents infinite loops
- **Cycle detection** prevents circular includes

📖 [Full Guide](docs/includes.md)

### API Reference

| Phase | Endpoint | Description |
|-------|----------|-------------|
| Browse | `POST /skills/browse` | Metadata only (lightweight discovery) |
| Load | `POST /skills/use` | Full rendered content |
| Resources | `GET /skills/{name}/resources` | List available extras |
| Resource | `POST /skills/resource` | Load specific resource |

All endpoints support scoping context (`active_paths`, `languages`) for accurate matching.

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License
AGPL-3.0 © [SergioC](https://github.com/sergioc)
