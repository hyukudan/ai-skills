# ChatGPT Integration

This guide explains how to use aiskills with ChatGPT, including Custom GPTs and the API.

## Option 1: Custom GPT with Actions

Create a Custom GPT that can search and read skills.

### Setup

1. **Start the aiskills API server:**
```bash
aiskills api serve
```

2. **Expose the server** (for production, use a proper deployment):
```bash
# Development: Use ngrok
ngrok http 8420

# Production: Deploy to cloud (Railway, Render, Fly.io, etc.)
```

3. **Create Custom GPT:**
   - Go to https://chat.openai.com/gpts/editor
   - Configure name and description
   - Go to "Configure" → "Actions"
   - Import OpenAPI schema from `https://your-server/docs/json`

### OpenAPI Schema

The API automatically generates an OpenAPI schema at `/docs`. You can also get the simplified tool definitions at `/openai/tools`.

### Available Actions

| Action | Description |
|--------|-------------|
| `skill_search` | Search for skills by query |
| `skill_read` | Read a skill's content |
| `skill_list` | List all available skills |
| `skill_suggest` | Get skill suggestions |

### Example Custom GPT Instructions

```
You are an AI assistant with access to a skills library. When users ask about coding topics:

1. Use skill_search to find relevant skills
2. Use skill_read to get the full skill content
3. Apply the skill's guidance to help the user

Always search for skills before answering complex coding questions.
```

## Option 2: API Integration

Use the REST API directly in your applications.

### Endpoints

```bash
# List skills
curl https://your-server/skills

# Search skills
curl -X POST https://your-server/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query": "debugging python"}'

# Read a skill
curl https://your-server/skills/python-debugging

# With variables
curl -X POST https://your-server/skills/read \
  -H "Content-Type: application/json" \
  -d '{"name": "template-skill", "variables": {"lang": "javascript"}}'
```

### Function Calling Format

Get OpenAI-compatible function definitions:

```bash
curl https://your-server/openai/tools
```

Use in your OpenAI API calls:

```python
import openai
import requests

# Get tools from aiskills
tools_response = requests.get("https://your-server/openai/tools")
tools = tools_response.json()["tools"]

# Use with OpenAI
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Help me debug this Python error"}],
    tools=tools,
)

# Handle function calls
if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        result = requests.post(
            "https://your-server/openai/call",
            json={
                "name": call.function.name,
                "arguments": json.loads(call.function.arguments)
            }
        )
        # Use result.json() to get the skill data
```

## Option 3: Assistants API

Use with OpenAI Assistants API:

```python
from openai import OpenAI
import requests

client = OpenAI()

# Get tools
tools = requests.get("https://your-server/openai/tools").json()["tools"]

# Create assistant with tools
assistant = client.beta.assistants.create(
    name="Skill-Enhanced Assistant",
    instructions="You have access to a skills library. Use it to help users.",
    model="gpt-4-turbo",
    tools=tools,
)
```

## Best Practices

1. **Index your skills** before using search:
   ```bash
   aiskills search-index index
   ```

2. **Use semantic search** for natural language queries

3. **Cache skill content** if making frequent requests

4. **Deploy securely** - use HTTPS and authentication in production

## Troubleshooting

### Skills not found
- Ensure skills are installed: `aiskills list`
- Re-index: `aiskills search-index index --rebuild`

### Search returns no results
- Check if search extras are installed: `pip install aiskills[search]`
- Use text search as fallback: `{"text_only": true}`

### Connection refused
- Verify server is running: `aiskills api serve`
- Check port: default is 8420
