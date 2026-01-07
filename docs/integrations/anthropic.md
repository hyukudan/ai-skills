# Anthropic Claude Integration

Use AI Skills with Claude models via the Anthropic API.

## Quick Start

```bash
pip install aiskills[anthropic]
```

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client()
response = client.chat("Help me debug this memory leak in Python")
print(response)
```

## Setup

### API Key

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or pass it directly:

```python
client = create_anthropic_client(api_key="sk-ant-...")
```

## Usage Examples

### Simple Chat

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client()

# Claude will automatically use skills when helpful
response = client.chat("How do I write better unit tests?")
print(response)
```

### With Custom Model

```python
# Use Claude 3 Opus for complex tasks
client = create_anthropic_client(model="claude-3-opus-20240229")

# Use Claude 3 Haiku for faster responses
client = create_anthropic_client(model="claude-3-haiku-20240307")

# Default is Claude 3.5 Sonnet
client = create_anthropic_client()  # claude-sonnet-4-20250514
```

### Multi-Turn Conversation

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client()

messages = [
    {"role": "user", "content": "What debugging skills do you have?"}
]

response = client.chat_with_messages(messages)
print(response)

# Continue the conversation
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "Show me the Python one"})

response = client.chat_with_messages(messages)
print(response)
```

### With System Prompt

```python
response = client.chat(
    "Help me optimize my SQL queries",
    system_prompt="You are a database expert. Be concise."
)
```

### Manual Tool Handling

For full control over tool execution:

```python
from aiskills.integrations import create_anthropic_client

# Disable auto-execution
client = create_anthropic_client(auto_execute=False)

# Get raw response with tool calls
response = client.get_completion_with_skills(
    messages=[{"role": "user", "content": "What skills are available?"}]
)

# Check for tool use
for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {block.input}")

        # Execute manually
        result = client.execute_tool(block.name, block.input)
        print(f"Result: {result}")
```

### Using Tools Directly

```python
from aiskills.integrations import get_anthropic_tools
from anthropic import Anthropic

# Get tools for your own Anthropic client
tools = get_anthropic_tools()

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Help me with testing"}],
    tools=tools,
)
```

## Available Tools

The integration provides these tools to Claude:

| Tool | Description |
|------|-------------|
| `use_skill` | Find and use the best matching skill for a task |
| `skill_search` | Search for skills by query |
| `skill_read` | Read a specific skill by name |
| `skill_list` | List all available skills |
| `skill_browse` | Browse skills with context filtering |

## CLI Testing

Test your Anthropic integration from the command line:

```bash
# Check if Anthropic is installed
aiskills llm status

# Test with default message
aiskills llm anthropic

# Test with custom message
aiskills llm anthropic "Explain caching strategies"

# Use a specific model
aiskills llm anthropic "Help me debug" --model claude-3-opus-20240229
```

## Configuration Options

```python
client = create_anthropic_client(
    api_key=None,           # Uses ANTHROPIC_API_KEY env var
    model="claude-sonnet-4-20250514",  # Model to use
    auto_execute=True,      # Auto-execute tool calls
    max_tokens=4096,        # Max tokens in response
)
```

## How It Works

1. You send a message to Claude
2. Claude recognizes when a skill would help and makes a tool call
3. The tool call is executed automatically (searches/loads skills)
4. Results are sent back to Claude
5. Claude generates the final response using the skill content

```
User: "How do I debug memory leaks?"
  ↓
Claude: tool_use(use_skill, context="debug memory leaks python")
  ↓
Tool: Returns python-debugging skill content
  ↓
Claude: Generates response using skill knowledge
```

## Error Handling

```python
from aiskills.integrations import create_anthropic_client

client = create_anthropic_client()

try:
    response = client.chat("Help me with testing")
except ImportError:
    print("Install with: pip install aiskills[anthropic]")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Use appropriate models**: Haiku for simple queries, Sonnet for balanced performance, Opus for complex reasoning
2. **Set max_tokens appropriately**: Higher values for detailed responses
3. **Provide context**: Claude uses context to select the right skills
4. **Handle rate limits**: Anthropic has rate limits; implement retry logic for production
