# LLM Provider Comparison

This guide compares the four LLM providers supported by AI Skills: OpenAI, Anthropic, Google Gemini, and Ollama.

## Feature Matrix

| Feature | OpenAI | Anthropic | Gemini | Ollama |
|---------|--------|-----------|--------|--------|
| **Tool/Function Calling** | Yes | Yes | Yes | Yes* |
| **Streaming** | Yes | Yes | Yes | Yes |
| **Auto Tool Execution** | Yes | Yes | Yes | Yes |
| **Max Tool Rounds** | Configurable | Configurable | N/A** | Configurable |
| **Local/Private** | No | No | No | Yes |
| **API Key Required** | Yes | Yes | Yes | No |
| **Async Support** | Yes | Yes | Yes | Yes |

*Ollama tool calling depends on model (llama3.1, mistral-nemo, mixtral support it)
**Gemini handles tool loops internally via SDK

---

## API Consistency

All providers share a consistent interface:

```python
# Same pattern works for all providers
from aiskills.integrations import create_<provider>_client

client = create_<provider>_client()
response = client.chat("Your question")
response = client.chat_with_messages(messages)
response = client.chat_stream("Your question")  # Generator

# Manual tool handling
result = client.execute_tool("tool_name", {"arg": "value"})
tools = client.get_tools()
```

---

## Provider Details

### OpenAI

**Best for:** General-purpose tasks, code generation, structured output

```python
from aiskills.integrations import create_openai_client

client = create_openai_client(
    model="gpt-4",           # or "gpt-4-turbo", "gpt-3.5-turbo"
    auto_execute=True,       # Auto-execute tool calls
    max_tool_rounds=5,       # Prevent infinite loops
)
```

**Models:**
- `gpt-4` - Most capable, slower
- `gpt-4-turbo` - Fast, cost-effective
- `gpt-3.5-turbo` - Fastest, cheapest

**Tool Format:** JSON Schema (OpenAI function calling format)

**Pricing:** ~$0.01-0.03 per 1K tokens (varies by model)

---

### Anthropic Claude

**Best for:** Code analysis, reasoning, long documents

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client(
    model="claude-sonnet-4-20250514",  # Default
    auto_execute=True,
    max_tool_rounds=5,
    max_tokens=4096,
)
```

**Models:**
- `claude-3-opus-20240229` - Most capable
- `claude-sonnet-4-20250514` - Balanced (default)
- `claude-3-haiku-20240307` - Fastest

**Tool Format:** Anthropic tool use format (`input_schema`)

**Pricing:** ~$0.003-0.015 per 1K tokens (varies by model)

---

### Google Gemini

**Best for:** Multimodal tasks, Google ecosystem integration

```python
from aiskills.integrations import create_gemini_client

client = create_gemini_client(
    model_name="gemini-1.5-pro",       # Default
    auto_function_calling=True,
)
```

**Models:**
- `gemini-1.5-pro` - Most capable (default)
- `gemini-1.5-flash` - Faster, cheaper

**Tool Format:** Python callables (native Gemini format)

**Pricing:** Free tier available, then ~$0.00025 per 1K tokens

**Note:** Gemini handles function calling loops internally via the SDK.

---

### Ollama (Local)

**Best for:** Privacy, offline use, no API costs

```python
from aiskills.integrations import create_ollama_client

client = create_ollama_client(
    model="llama3.1",        # Default
    host=None,               # Uses localhost:11434
    use_tools=None,          # Auto-detect based on model
    max_tool_rounds=5,
)
```

**Tool-Capable Models:**
- `llama3.1` - Meta's latest (recommended)
- `llama3.2` - Smaller variants
- `mistral-nemo` - Mistral's tool-capable
- `mixtral` - Mixture of experts
- `qwen2.5` - Alibaba's model

**Non-Tool Models (use prompt injection):**
- `codellama` - Code-specialized
- `llama3` - General purpose
- Any other Ollama model

**Tool Format:** OpenAI-compatible JSON Schema

**Pricing:** Free (runs locally)

**Unique Features:**
- `chat_with_skill()` - Prompt injection for non-tool models
- `generate_with_skill()` - Non-chat completion mode
- `is_model_available()` - Check model availability
- `list_local_models()` - List installed models

---

## Choosing a Provider

### Decision Tree

```
Need local/private processing?
├─ Yes → Ollama
└─ No → Need multimodal (images)?
         ├─ Yes → Gemini
         └─ No → Need best code analysis?
                  ├─ Yes → Anthropic Claude
                  └─ No → OpenAI (general purpose)
```

### Use Case Recommendations

| Use Case | Recommended Provider | Reason |
|----------|---------------------|--------|
| Code generation | Anthropic, OpenAI | Strong code understanding |
| Code review | Anthropic | Excellent analysis |
| Documentation | OpenAI, Anthropic | Good at structured output |
| Quick prototyping | Gemini (free tier) | Cost-effective |
| Privacy-sensitive | Ollama | Fully local |
| Offline usage | Ollama | No internet required |
| Production API | OpenAI, Anthropic | Reliable, scalable |
| Multimodal | Gemini | Native image support |

---

## Error Handling

All providers use consistent error types:

```python
from aiskills.integrations import (
    AISkillsError,        # Base exception
    ProviderError,        # API errors
    RateLimitError,       # 429 errors (retryable)
    ToolExecutionError,   # Tool failures
    ToolValidationError,  # Invalid arguments
    SkillNotFoundError,   # Skill not found
)

try:
    response = client.chat("...")
except RateLimitError as e:
    print(f"Rate limited by {e.provider}, retry after {e.retry_after}s")
except ProviderError as e:
    print(f"Provider {e.provider} error: {e.status_code}")
except ToolValidationError as e:
    print(f"Invalid args for {e.tool_name}: {e.invalid_args}")
```

---

## Async Support

All providers support async/await for non-blocking operations:

```python
import asyncio
from aiskills.integrations import create_openai_client

async def main():
    client = create_openai_client()

    # Async chat
    response = await client.chat_async("Help me debug Python")

    # Async with messages
    messages = [{"role": "user", "content": "Explain testing"}]
    response = await client.chat_with_messages_async(messages)

    # Async streaming
    async for chunk in client.chat_stream_async("Write a test"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

**Async Methods Available:**
- `chat_async()` - Non-blocking single message
- `chat_with_messages_async()` - Non-blocking multi-turn
- `chat_stream_async()` - Async streaming response

---

## Multi-Provider Patterns

### Fallback Chain

```python
providers = ["openai", "anthropic", "gemini", "ollama"]
factories = {
    "openai": create_openai_client,
    "anthropic": create_anthropic_client,
    "gemini": create_gemini_client,
    "ollama": lambda: create_ollama_client(model="llama3.1"),
}

for name in providers:
    try:
        client = factories[name]()
        return client.chat(question)
    except Exception:
        continue

raise Exception("All providers failed")
```

### Parallel Queries

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def query_all(question):
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(client.chat, question): name
            for name, client in clients.items()
        }
        for future in as_completed(futures, timeout=30):
            name = futures[future]
            results[name] = future.result()
    return results
```

### Task-Based Routing

```python
TASK_PROVIDERS = {
    "code": ["anthropic", "openai"],
    "creative": ["anthropic", "gemini"],
    "analysis": ["openai", "anthropic"],
    "fast": ["gemini", "ollama"],
    "local": ["ollama"],
}

def smart_query(question, task_type="code"):
    for provider in TASK_PROVIDERS[task_type]:
        if provider in available_clients:
            return available_clients[provider].chat(question)
```

---

## See Also

- [Examples README](../examples/README.md) - Code examples
- [SDK Integration Guide](sdk.md) - Detailed SDK documentation
- [Multi-Provider Example](../examples/multi_provider.py) - Full implementation
