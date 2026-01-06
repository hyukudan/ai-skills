# Platform Integrations

aiskills is designed to be **LLM-agnostic**. This directory contains integration guides for various platforms.

## Supported Platforms

| Platform | Integration Method | Guide |
|----------|-------------------|-------|
| **Claude Code** | Plugin + MCP | [/plugin](../../plugin/README.md) |
| **Claude Desktop** | MCP Server | [README](../../README.md#mcp-server) |
| **ChatGPT / Custom GPTs** | REST API + Actions | [chatgpt.md](./chatgpt.md) |
| **Google Gemini** | REST API + Function Calling | [gemini.md](./gemini.md) |
| **Other LLMs** | REST API | [other-llms.md](./other-llms.md) |

## Quick Comparison

### For Claude Ecosystem
Use **MCP Server** - native protocol, best integration:
```bash
aiskills mcp serve
```

### For OpenAI/ChatGPT
Use **REST API** with OpenAI-compatible tools:
```bash
aiskills api serve
# Get tools at: http://localhost:8420/openai/tools
```

### For Other LLMs
Use **REST API** directly:
```bash
aiskills api serve
# Endpoints at: http://localhost:8420/
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      aiskills                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐ │
│  │   CLI   │  │   MCP   │  │       REST API          │ │
│  │         │  │ Server  │  │ (OpenAI-compatible)     │ │
│  └────┬────┘  └────┬────┘  └───────────┬─────────────┘ │
│       │            │                    │               │
│       └────────────┴────────────────────┘               │
│                         │                               │
│              ┌──────────┴──────────┐                    │
│              │    Core Engine      │                    │
│              │  - Skill Manager    │                    │
│              │  - Registry         │                    │
│              │  - Search           │                    │
│              └─────────────────────┘                    │
└─────────────────────────────────────────────────────────┘
         │              │                 │
         ▼              ▼                 ▼
   Claude Code    Claude Desktop    ChatGPT/Gemini/
     Plugin       (via MCP)         LangChain/etc
```

## Feature Matrix

| Feature | CLI | MCP | REST API |
|---------|-----|-----|----------|
| List skills | ✅ | ✅ | ✅ |
| Read skills | ✅ | ✅ | ✅ |
| Search (semantic) | ✅ | ✅ | ✅ |
| Search (text) | ✅ | ✅ | ✅ |
| Suggest skills | ❌ | ✅ | ✅ |
| Install skills | ✅ | ❌ | ❌ |
| Variable rendering | ✅ | ✅ | ✅ |
| OpenAI format | ❌ | ❌ | ✅ |
| Swagger docs | ❌ | ❌ | ✅ |

## Deployment

For production use:

1. **Local development**: Run directly
2. **Cloud deployment**: Use Docker or your preferred platform
3. **Enterprise**: Consider Kubernetes with authentication

See [other-llms.md](./other-llms.md#deployment-options) for detailed deployment guides.
