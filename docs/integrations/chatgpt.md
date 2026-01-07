# OpenAI / ChatGPT Integration

**Ai Skills** provides seamless integration with OpenAI models (GPT-4, GPT-3.5, Codex) via the built-in SDK wrapper or REST API.

## Quick Start (Recommended)

```bash
pip install aiskills[search] openai
```

```python
from aiskills.integrations import create_openai_client

# Create client with automatic tool execution
client = create_openai_client(model="gpt-4")

# Chat - skills are invoked automatically when needed
response = client.chat("Help me debug a memory leak in Python")
print(response)
```

The client automatically:
- Configures OpenAI with skill tools
- Executes tool calls in a loop
- Returns the final response

## Configuration Options

```python
from aiskills.integrations import create_openai_client

client = create_openai_client(
    api_key="sk-...",           # Or use OPENAI_API_KEY env var
    model="gpt-4-turbo",        # Default: gpt-4
    auto_execute=True,          # Auto-execute tool calls (default: True)
    max_tool_rounds=5,          # Prevent infinite loops
)
```

## Manual Tool Handling

For full control over tool execution:

```python
from aiskills.integrations import create_openai_client

client = create_openai_client(auto_execute=False)

# Get raw completion with tool calls
response = client.get_completion_with_skills(
    messages=[{"role": "user", "content": "Help with testing"}],
)

# Handle tool calls yourself
if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        result = client.execute_tool(
            call.function.name,
            json.loads(call.function.arguments)
        )
        print(f"Tool {call.function.name}: {result}")
```

## Using with Existing OpenAI Client

```python
from openai import OpenAI
from aiskills.integrations import get_openai_tools, OpenAISkills

# Get tool definitions
tools = get_openai_tools()

# Use with your own client
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Help me debug"}],
    tools=tools,
)

# Execute tool calls via integration
integration = OpenAISkills()
for call in response.choices[0].message.tool_calls or []:
    result = integration.execute_tool(
        call.function.name,
        json.loads(call.function.arguments)
    )
```

## Custom GPT with Actions

For ChatGPT Custom GPTs:

1. **Start the API server:**
```bash
aiskills api serve
```

2. **Expose publicly** (for production):
```bash
# Development: Use ngrok
ngrok http 8420

# Production: Deploy to Railway, Render, Fly.io, etc.
```

3. **Configure Custom GPT:**
   - Go to https://chat.openai.com/gpts/editor
   - Configure → Actions
   - Import OpenAPI schema from `https://your-server/docs`

### Custom GPT Instructions

```
You have access to AI Skills - a library of expert coding guides.

When users ask about coding, debugging, or best practices:
1. Use use_skill to find relevant guidance
2. Apply the skill's advice to the user's specific problem
3. Mention which skill you used for transparency

Available tools:
- use_skill: Find the best skill for a task (describe naturally)
- skill_search: Search for skills by topic
- skill_read: Read a specific skill by name
- skill_list: List all available skills
```

## Assistants API

```python
from openai import OpenAI
from aiskills.integrations import get_openai_tools

client = OpenAI()
tools = get_openai_tools()

# Create assistant with skills
assistant = client.beta.assistants.create(
    name="Skill-Enhanced Assistant",
    instructions="Use skills to help users with coding tasks.",
    model="gpt-4-turbo",
    tools=tools,
)
```

## REST API

For non-Python environments:

```bash
# Start server
aiskills api serve

# Get OpenAI-compatible tools
curl http://localhost:8420/openai/tools

# Execute function call
curl -X POST http://localhost:8420/openai/call \
  -H "Content-Type: application/json" \
  -d '{"name": "use_skill", "arguments": {"context": "debug python"}}'
```

## Available Tools

| Tool | Description |
|------|-------------|
| `use_skill` | Find and use the best skill for a task |
| `skill_search` | Search skills by semantic similarity |
| `skill_read` | Read a specific skill by name |
| `skill_list` | List all available skills |
| `skill_suggest` | Get skill suggestions for context |

## Example: Code Review Bot

```python
from aiskills.integrations import create_openai_client

client = create_openai_client(model="gpt-4")

response = client.chat("""
Review this code and suggest improvements:

def fetch_users():
    users = []
    for i in range(1000):
        response = requests.get(f"/api/users/{i}")
        users.append(response.json())
    return users
""")

print(response)
# GPT-4 will use skills like "code-review" or "python-best-practices"
```

## Supported Models

- **gpt-4**, **gpt-4-turbo** - Best quality, recommended
- **gpt-4o**, **gpt-4o-mini** - Latest models
- **gpt-3.5-turbo** - Faster, good for simple queries
- **o1**, **o1-mini** - Reasoning models (limited tool support)

## Troubleshooting

### Rate limits
- Use `gpt-3.5-turbo` for development
- Implement retry logic with exponential backoff

### Tool calls not working
- Ensure `tools` parameter is passed to the API
- Check that skill content isn't too long (context limits)

### Connection issues
- Verify `OPENAI_API_KEY` is set
- Check OpenAI API status: https://status.openai.com
