# Ollama & Local LLM Integration

**Ai Skills** provides excellent support for local LLMs via Ollama. The built-in SDK wrapper handles tool calling automatically, with fallback options for models that don't support it.

## Quick Start (Recommended)

```bash
pip install aiskills[search] ollama
```

```python
from aiskills.integrations import create_ollama_client

# Create client - auto-detects tool calling support
client = create_ollama_client(model="llama3.1")

# Chat with automatic skill invocation
response = client.chat("Help me debug a memory leak in Python")
print(response)
```

The client automatically:
- Detects if your model supports tool calling
- Executes skill lookups when the model requests them
- Falls back to prompt injection for non-tool models

## Tool Calling vs Prompt Injection

### Models with Tool Calling (Recommended)

These models support native tool/function calling:
- **llama3.1**, **llama3.2** - Excellent support
- **mistral**, **mixtral** - Good support
- **qwen2**, **qwen2.5** - Strong support
- **command-r**, **command-r-plus** - Native support

```python
from aiskills.integrations import create_ollama_client

# Tool calling is auto-enabled for supported models
client = create_ollama_client(model="llama3.1")
response = client.chat("How do I write unit tests in Python?")
```

### Models without Tool Calling

For models like `codellama`, use prompt injection:

```python
from aiskills.integrations import create_ollama_client

# Disable tools, use prompt injection instead
client = create_ollama_client(model="codellama", use_tools=False)

# Skill is loaded into context automatically
response = client.chat_with_skill(
    skill_query="python unit testing",
    user_message="Write tests for this function: def add(a, b): return a + b"
)
```

## CLI Pipelining

For quick one-off queries:

```bash
# Find and pipe skill content to Ollama
aiskills use "debug python memory leak" | ollama run llama3 "Apply this to my code"

# Search and read specific skill
SKILL=$(aiskills search "linux networking" --limit 1 --name-only)
aiskills read $SKILL | ollama run llama3 "How do I check open ports?"
```

## Manual Tool Integration

For full control:

```python
from aiskills.integrations import get_ollama_tools
import ollama

# Get tool definitions
tools = get_ollama_tools()

# Use with ollama.chat directly
response = ollama.chat(
    model='llama3.1',
    messages=[{'role': 'user', 'content': 'Help me debug this code'}],
    tools=tools,
)

# Handle tool calls manually if needed
if response['message'].get('tool_calls'):
    # Process tool calls...
    pass
```

## Configuration Options

```python
from aiskills.integrations import create_ollama_client

client = create_ollama_client(
    model="llama3.1",           # Model name
    host="http://localhost:11434",  # Ollama server (default)
    use_tools=True,             # Auto-detected if None
    max_tool_rounds=5,          # Prevent infinite loops
)
```

## Available Tools

| Tool | Description |
|------|-------------|
| `use_skill` | Find and use the best skill for a task |
| `skill_search` | Search skills by query |
| `skill_read` | Read a specific skill by name |
| `skill_list` | List all available skills |
| `skill_browse` | Browse skills with metadata |

## Generation Mode

For completions (non-chat):

```python
from aiskills.integrations import create_ollama_client

client = create_ollama_client(model="codellama", use_tools=False)

# Generate with skill context
code = client.generate_with_skill(
    skill_query="python unit testing",
    prompt="Write pytest tests for: def multiply(a, b): return a * b"
)
```

## REST API Alternative

For any language:

```bash
# Start server
aiskills api serve

# Get skill via HTTP
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{"context": "optimize SQL queries"}'
```

## Example: Interactive Agent

```python
from aiskills.integrations import create_ollama_client

client = create_ollama_client(model="llama3.1")

# Simple chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    response = client.chat(user_input)
    print(f"Bot: {response}\n")
```

## Checking Model Availability

```python
from aiskills.integrations import create_ollama_client

client = create_ollama_client(model="llama3.1")

# Check if model is available
if client.is_model_available():
    response = client.chat("Hello!")
else:
    print("Model not installed. Run: ollama pull llama3.1")

# List all local models
models = client.list_local_models()
for model in models:
    print(f"- {model['name']}")
```

## Troubleshooting

### Tool calls not working
- Ensure you're using a tool-capable model (llama3.1, mistral, etc.)
- Try `use_tools=True` to force tool mode
- Check Ollama version: `ollama --version` (need 0.1.24+)

### Model not found
- Pull the model: `ollama pull llama3.1`
- Check available models: `ollama list`

### Slow responses
- Use smaller models for faster inference
- Consider `gemma2:2b` for quick responses
- Use `chat_with_skill()` instead of tool calling for simpler flows
