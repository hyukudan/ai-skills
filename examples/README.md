# AI Skills Examples

This directory contains examples demonstrating how to use AI Skills with various LLM providers.

## Quick Start

```bash
# Install AI Skills with all LLM integrations
pip install aiskills[llms]

# Or install for specific providers
pip install aiskills[openai]      # OpenAI GPT models
pip install aiskills[anthropic]   # Anthropic Claude
pip install aiskills[gemini]      # Google Gemini
pip install aiskills[ollama]      # Ollama local models
```

## Examples Overview

### Jupyter Notebooks

Located in `notebooks/`:

| Notebook | Provider | Description |
|----------|----------|-------------|
| [`openai_quickstart.ipynb`](notebooks/openai_quickstart.ipynb) | OpenAI | Getting started with GPT-4 and skills |
| [`anthropic_claude.ipynb`](notebooks/anthropic_claude.ipynb) | Anthropic | Claude 3.5/3 with tool use |
| [`gemini_colab.ipynb`](notebooks/gemini_colab.ipynb) | Google | Gemini with function calling |
| [`ollama_local.ipynb`](notebooks/ollama_local.ipynb) | Ollama | Local models with llama3.1 |

### Python Scripts

| Script | Description |
|--------|-------------|
| [`multi_provider.py`](multi_provider.py) | Multi-provider orchestration patterns |

### Example Skills

Located in `skills/`:

30+ example skills covering Python debugging, testing strategies, Docker/Kubernetes, authentication patterns, and more.

---

## Running the Examples

### Prerequisites

1. **API Keys** (set as environment variables):

   ```bash
   # OpenAI
   export OPENAI_API_KEY="sk-..."

   # Anthropic Claude
   export ANTHROPIC_API_KEY="sk-ant-..."

   # Google Gemini
   export GEMINI_API_KEY="..."
   # or
   export GOOGLE_API_KEY="..."
   ```

2. **Ollama** (for local models):

   ```bash
   # Install Ollama: https://ollama.ai
   ollama pull llama3.1
   ```

### Running Notebooks

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook examples/notebooks/

# Or use VS Code with Jupyter extension
```

### Running Multi-Provider Script

```bash
python examples/multi_provider.py
```

**Expected output:**
```
============================================================
AI Skills Multi-Provider Demo
============================================================

Available providers:
  openai: YES
  anthropic: YES
  gemini: YES
  ollama: no

Using 3 provider(s): openai, anthropic, gemini

============================================================
DEMO 1: Compare Providers
...
```

---

## Code Examples

### Basic Usage (Any Provider)

```python
from aiskills.integrations import create_openai_client

# Create client
client = create_openai_client()

# Chat with automatic skill discovery
response = client.chat("Help me debug a Python memory leak")
print(response)
```

### Multi-Turn Conversation

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client()

# First message
response1 = client.chat("What skills do you have for testing?")
print(response1)

# Continue with context
messages = [
    {"role": "user", "content": "What skills do you have for testing?"},
    {"role": "assistant", "content": response1},
    {"role": "user", "content": "Tell me more about unit testing"},
]
response2 = client.chat_with_messages(messages)
print(response2)
```

### Streaming Responses

```python
from aiskills.integrations import create_gemini_client

client = create_gemini_client()

# Stream response chunks
for chunk in client.chat_stream("Explain async/await in Python"):
    print(chunk, end="", flush=True)
```

### Multi-Provider Fallback

```python
from aiskills.integrations import (
    create_openai_client,
    create_anthropic_client,
    create_ollama_client,
)

# Try providers in order
providers = [
    ("openai", create_openai_client),
    ("anthropic", create_anthropic_client),
    ("ollama", lambda: create_ollama_client(model="llama3.1")),
]

for name, factory in providers:
    try:
        client = factory()
        response = client.chat("Help me debug Python")
        print(f"[{name}] Success!")
        break
    except Exception as e:
        print(f"[{name}] Failed: {e}")
```

### Manual Tool Handling

```python
from aiskills.integrations import create_openai_client

client = create_openai_client(auto_execute=False)

# Get raw completion with tool calls
response = client.get_completion_with_skills(
    messages=[{"role": "user", "content": "Find Python debugging skills"}]
)

# Handle tool calls manually
for choice in response.choices:
    for tool_call in choice.message.tool_calls or []:
        result = client.execute_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        print(f"Tool result: {result}")
```

---

## Provider Comparison

| Feature | OpenAI | Anthropic | Gemini | Ollama |
|---------|--------|-----------|--------|--------|
| Tool/Function Calling | Yes | Yes | Yes | Yes* |
| Streaming | Yes | Yes | Yes | Yes |
| `chat()` | Yes | Yes | Yes | Yes |
| `chat_with_messages()` | Yes | Yes | Yes | Yes |
| `chat_stream()` | Yes | Yes | Yes | Yes |
| Auto Tool Execution | Yes | Yes | Yes | Yes |
| Local | No | No | No | Yes |
| API Key Required | Yes | Yes | Yes | No |

*Ollama tool calling depends on model (llama3.1, mistral-nemo support it)

---

## Troubleshooting

### "No module named 'openai'"

Install the provider-specific package:
```bash
pip install aiskills[openai]
```

### "API key not found"

Set the environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### "Ollama model not found"

Pull the model first:
```bash
ollama pull llama3.1
```

### Rate Limits

The SDK includes retry logic with exponential backoff. For heavy usage, consider:
- Using fallback providers
- Implementing request queuing
- Checking your API tier limits

---

## See Also

- [Main README](../README.md) - Project overview
- [SDK Integration Guide](../docs/sdk.md) - Detailed SDK documentation
- [Provider Comparison](../docs/provider-comparison.md) - Detailed comparison
