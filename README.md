# Ai Skills

![Ai Skills Header](./docs/assets/ai_skills_header_vibrant.png)

<div align="center">

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://python.org)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](https://github.com/sergioc/ai-skills)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange?style=flat-square)](https://pypi.org/project/aiskills)

**Universal AI Knowledge for Everyone**
*Write skills once. Use them with Claude, ChatGPT, Gemini, and Ollama.*

[Quick Start](#quick-start) • [Why Ai Skills](#-why-ai-skills) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

**Ai Skills** is a local-first skills management system that serves **any large language model**. It transforms static markdown files into dynamic, semantically searchable tools that your AI agents can use to solve complex problems.

## 🚀 Quick Start

Get started in seconds.

1. **Install**
   ```bash
   pip install aiskills[all]
   ```

2. **Initialize**
   ```bash
   aiskills init my-first-skill
   ```

3. **Search**
   ```bash
   aiskills search "how to debug python"
   # Returns specific debugging skills based on semantic meaning
   ```

## ✨ Why Ai Skills?

*   **🌍 Universal Compatibility** – One skill library for Claude, ChatGPT, Gemini, and local LLMs. Stop rewriting prompts.
*   **🧠 Semantic Intelligence** – Find the right skill by meaning, not just keywords. "Fix error" finds `debugging.md`.
*   **🔌 Plug-and-Play** – Works as an MCP Server for Claude Desktop, an API for custom agents, or a CLI tool.
*   **🔒 Local & Private** – Your knowledge base stays on your disk. No cloud vector DBs required.
*   **🧩 Composable** – Skills can import other skills, enforcing DRY (Don't Repeat Yourself) for AI prompts.

## 🏗️ Architecture

Ai Skills sits between your AI clients and your knowledge base, ensuring the right context is delivered every time.

```mermaid
graph TD
    subgraph Clients
        Claude[Claude Desktop]
        GPT[ChatGPT / Custom GPTs]
        Gemini[Google Gemini]
        Agent[Custom Agents]
    end

    subgraph "Ai Skills Core"
        MCP[MCP Server]
        API[REST API]
        CLI[CLI Tool]
        Engine[Skill Engine]
        Search[Semantic Search]
    end

    subgraph "Local Storage"
        Skills["Skill Files (.md)"]
        Vectors["Vector Store (ChromaDB)"]
    end

    Claude -->|MCP Protocol| MCP
    GPT -->|HTTP| API
    Gemini -->|HTTP| API
    Agent -->|HTTP| API

    MCP --> Engine
    API --> Engine
    CLI --> Engine

    Engine -->|Read/Parse| Skills
    Engine -->|Query| Search
    Search -->|Retrieve| Vectors
    Skills -->|Index| Vectors
```

## 🛠️ Integrations

| Platform | Integration Method | Status | Guide |
| :--- | :--- | :--- | :--- |
| **Claude Desktop** | MCP Server | ✅ Ready | [Setup Guide](#mcp-server-claude-desktop) |
| **ChatGPT** | REST API (OpenAI Spec) | ✅ Ready | [ChatGPT Guide](docs/integrations/chatgpt.md) |
| **Claude Code** | Plugin | ✅ Ready | [Plugin Guide](plugin/README.md) |
| **Custom Agents** | Python SDK / CLI | ✅ Ready | [SDK Docs](docs/sdk.md) |

### MCP Server (Claude Desktop)
Add this to your `claude_desktop_config.json`:
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

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License
AGPL-3.0 © [SergioC](https://github.com/sergioc)
