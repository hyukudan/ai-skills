# Google Gemini Integration

**Ai Skills** provides first-class integration with Google Gemini models via the built-in SDK wrapper or manual function calling.

## Quick Start (Recommended)

The simplest way to use skills with Gemini:

```bash
pip install aiskills[search] google-generativeai
```

```python
from aiskills.integrations import create_gemini_client

# Create client with skills pre-configured
client = create_gemini_client()

# Chat with automatic function calling
response = client.chat("Help me debug a memory leak in Python")
print(response)
```

That's it! The client automatically:
- Configures Gemini with skill tools
- Enables automatic function calling
- Executes skill lookups when needed

## Alternative: Get Pre-configured Model

If you need more control over the chat session:

```python
from aiskills.integrations import create_gemini_model

# Get a GenerativeModel with tools attached
model = create_gemini_model(model_name="gemini-1.5-pro")

# Start chat with auto function calling
chat = model.start_chat(enable_automatic_function_calling=True)

# Multi-turn conversation
response1 = chat.send_message("What skills do you have for testing?")
response2 = chat.send_message("Show me the Python debugging one")
```

## Manual Integration

For full control, use the tools directly:

```python
from aiskills.integrations import get_gemini_tools
import google.generativeai as genai

# Get skill functions
tools = get_gemini_tools()

# Create your own model
genai.configure(api_key="your-api-key")
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=tools,
)

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("Help me with database optimization")
```

## Available Tools

The integration provides these tools to Gemini:

| Tool | Description |
|------|-------------|
| `use_skill` | Find and use the best skill for a task |
| `skill_search` | Search skills by semantic similarity |
| `skill_read` | Read a specific skill by name |
| `skill_list` | List all available skills |
| `skill_browse` | Browse skills with metadata (lightweight) |

## HTTP API Alternative

If not using Python, run the REST API:

```bash
aiskills api serve
# Endpoint: http://localhost:8420
```

Then configure Gemini to call your endpoints. The `/openai/tools` endpoint provides function definitions compatible with most frameworks.

## Configuration Options

```python
from aiskills.integrations import create_gemini_client

client = create_gemini_client(
    api_key="your-api-key",           # Or use GEMINI_API_KEY env var
    model_name="gemini-1.5-flash",    # Default: gemini-1.5-pro
    auto_function_calling=True,        # Default: True
)
```

## Example: Code Review Agent

```python
from aiskills.integrations import create_gemini_client

client = create_gemini_client()

# The client will automatically find and use relevant skills
response = client.chat("""
Review this code for potential issues:

def process_data(items):
    results = []
    for i in range(len(items)):
        results.append(items[i] * 2)
    return results
""")

print(response)
# Gemini will use skills like "code-review" or "python-best-practices"
# to provide informed feedback
```

## Supported Models

- **gemini-1.5-pro** - Best quality, recommended
- **gemini-1.5-flash** - Faster, good for simple queries
- **gemini-1.0-pro** - Legacy, basic support
