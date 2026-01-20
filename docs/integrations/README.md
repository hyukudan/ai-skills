# Platform Integrations

aiskills is designed to be **LLM-agnostic**. This directory contains integration guides for various platforms.

## Quick Start with SDK Wrappers

The easiest way to integrate with any LLM:

```bash
# Install with your preferred provider
pip install aiskills[openai]     # For OpenAI/ChatGPT
pip install aiskills[anthropic]  # For Anthropic Claude
pip install aiskills[gemini]     # For Google Gemini
pip install aiskills[ollama]     # For Ollama/local LLMs
pip install aiskills[llms]       # All providers
```

```python
# OpenAI
from aiskills.integrations import create_openai_client
client = create_openai_client()
response = client.chat("Help me debug this memory leak")

# Anthropic Claude
from aiskills.integrations import create_anthropic_client
client = create_anthropic_client()
response = client.chat("Help me write unit tests")

# Gemini
from aiskills.integrations import create_gemini_client
client = create_gemini_client()
response = client.chat("How do I optimize this SQL query?")

# Ollama
from aiskills.integrations import create_ollama_client
client = create_ollama_client(model="llama3.1")
response = client.chat("Explain async patterns in Python")
```

## Supported Platforms

| Platform | SDK Wrapper | REST API | Native Protocol |
|----------|-------------|----------|-----------------|
| **OpenAI / ChatGPT** | ✅ `create_openai_client()` | ✅ | - |
| **Anthropic Claude** | ✅ `create_anthropic_client()` | ✅ | - |
| **Google Gemini** | ✅ `create_gemini_client()` | ✅ | - |
| **Local LLMs (Ollama)** | ✅ `create_ollama_client()` | ✅ | - |
| **Claude Code** | - | - | ✅ Plugin + MCP |
| **Claude Desktop** | - | - | ✅ MCP Server |

## Integration Guides

| Platform | Guide | Method |
|----------|-------|--------|
| **OpenAI / ChatGPT** | [chatgpt.md](./chatgpt.md) | SDK wrapper or REST API |
| **Anthropic Claude** | [anthropic.md](./anthropic.md) | SDK wrapper or Tool Use |
| **Google Gemini** | [gemini.md](./gemini.md) | SDK wrapper or Function Calling |
| **Local LLMs (Ollama, vLLM)** | [ollama.md](./ollama.md) | SDK wrapper or CLI pipe |
| **Claude Code** | [/plugin](../../plugin/README.md) | Plugin + MCP |
| **Claude Desktop** | [claude_desktop.md](./claude_desktop.md) | MCP Server |
| **Other LLMs** | [other-llms.md](./other-llms.md) | REST API |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        aiskills                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              SDK Wrappers (Python)                       ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                 ││
│  │  │ OpenAI  │  │ Gemini  │  │ Ollama  │                 ││
│  │  └────┬────┘  └────┬────┘  └────┬────┘                 ││
│  └───────┼────────────┼────────────┼────────────────────────┘│
│          │            │            │                         │
│  ┌───────┴────────────┴────────────┴───────────────────────┐│
│  │                    Core Engine                           ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  ││
│  │  │  CLI    │  │   MCP   │  │REST API │  │  Router   │  ││
│  │  │         │  │ Server  │  │(OpenAI) │  │           │  ││
│  │  └─────────┘  └─────────┘  └─────────┘  └───────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
         │              │              │             │
         ▼              ▼              ▼             ▼
    Claude Code    Claude Desktop   Custom GPT    LangChain
      Plugin        (MCP)           Actions        Agents
```

## Feature Comparison

| Feature | SDK Wrappers | REST API | MCP | CLI |
|---------|--------------|----------|-----|-----|
| Auto tool execution | ✅ | Manual | ✅ | ❌ |
| Streaming | ⚠️ Provider-dependent | ❌ | ❌ | ❌ |
| Semantic search | ✅ | ✅ | ✅ | ✅ |
| Progressive disclosure | ✅ | ✅ | ✅ | ✅ |
| Variable rendering | ✅ | ✅ | ✅ | ✅ |
| OpenAI format | ✅ | ✅ | ❌ | ❌ |
| Swagger docs | ❌ | ✅ | ❌ | ❌ |

## Auto-Discovery API

The REST API includes an auto-discovery endpoint to help LLMs decide when to invoke skills:

```bash
curl -X POST http://localhost:8420/skills/should-invoke \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I have a memory leak in Python", "languages": ["python"]}'
```

Response:
```json
{
  "should_invoke": true,
  "suggested_skill": "python-debugging",
  "confidence": 0.87,
  "matched_triggers": ["memory leak"],
  "alternatives": ["error-diagnosis", "testing-strategies"]
}
```

## Deployment

For production use:

1. **Local development**: Use SDK wrappers directly
2. **Cloud deployment**: Run `aiskills api serve` with Docker
3. **Enterprise**: Kubernetes with authentication

See [other-llms.md](./other-llms.md#deployment-options) for detailed deployment guides.
