# Integration with Other LLMs

This guide covers integrating aiskills with various LLM providers and frameworks.

## Generic REST API Usage

The aiskills REST API works with any HTTP client.

### Base URL
```
http://localhost:8420
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/skills` | List all skills |
| GET | `/skills/{name}` | Get skill by name |
| POST | `/skills/search` | Search skills |
| POST | `/skills/read` | Read with variables |
| POST | `/skills/suggest` | Get suggestions |
| GET | `/openai/tools` | OpenAI-format tools |
| POST | `/openai/call` | Execute function |

### Example: cURL

```bash
# List skills
curl http://localhost:8420/skills

# Search
curl -X POST http://localhost:8420/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python debugging"}'

# Read skill
curl http://localhost:8420/skills/python-debugging
```

## Anthropic Claude (API)

```python
import anthropic
import requests

client = anthropic.Anthropic()

# Get tool definitions
tools_response = requests.get("http://localhost:8420/openai/tools")
openai_tools = tools_response.json()["tools"]

# Convert to Claude format
claude_tools = []
for tool in openai_tools:
    func = tool["function"]
    claude_tools.append({
        "name": func["name"],
        "description": func["description"],
        "input_schema": func["parameters"]
    })

# Use with Claude
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=claude_tools,
    messages=[
        {"role": "user", "content": "Help me debug Python code"}
    ]
)

# Handle tool use
for block in message.content:
    if block.type == "tool_use":
        result = requests.post(
            "http://localhost:8420/openai/call",
            json={"name": block.name, "arguments": block.input}
        ).json()
        # Continue conversation with result
```

## Ollama / Local Models

```python
import ollama
import requests

AISKILLS_URL = "http://localhost:8420"

def get_skill_context(query: str) -> str:
    """Get relevant skill content for context."""
    # Search for relevant skills
    search = requests.post(
        f"{AISKILLS_URL}/skills/search",
        json={"query": query, "limit": 2}
    ).json()

    context = ""
    for result in search["results"]:
        skill_name = result["skill"]["name"]
        # Get full content
        skill = requests.get(f"{AISKILLS_URL}/skills/{skill_name}").json()
        context += f"\n{skill['content']}\n"

    return context

# Use with Ollama
user_query = "How do I debug Python applications?"
skill_context = get_skill_context(user_query)

response = ollama.chat(
    model="llama3",
    messages=[
        {
            "role": "system",
            "content": f"Use this knowledge:\n{skill_context}"
        },
        {"role": "user", "content": user_query}
    ]
)
```

## LangChain

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import requests

AISKILLS_URL = "http://localhost:8420"

def skill_search(query: str) -> str:
    """Search for relevant skills."""
    response = requests.post(
        f"{AISKILLS_URL}/skills/search",
        json={"query": query, "limit": 5}
    )
    return str(response.json())

def skill_read(name: str) -> str:
    """Read a skill by name."""
    response = requests.get(f"{AISKILLS_URL}/skills/{name}")
    return response.json()["content"]

# Create tools
tools = [
    Tool(
        name="skill_search",
        func=skill_search,
        description="Search for AI skills by query"
    ),
    Tool(
        name="skill_read",
        func=skill_read,
        description="Read a skill's content by name"
    ),
]

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
result = agent.run("Find a skill about Python debugging and show me its content")
```

## LlamaIndex

```python
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
import requests

AISKILLS_URL = "http://localhost:8420"

def search_skills(query: str, limit: int = 5) -> dict:
    """Search for skills semantically."""
    response = requests.post(
        f"{AISKILLS_URL}/skills/search",
        json={"query": query, "limit": limit}
    )
    return response.json()

def read_skill(name: str) -> dict:
    """Read skill content."""
    response = requests.get(f"{AISKILLS_URL}/skills/{name}")
    return response.json()

# Create tools
tools = [
    FunctionTool.from_defaults(fn=search_skills),
    FunctionTool.from_defaults(fn=read_skill),
]

# Create agent
agent = OpenAIAgent.from_tools(tools, verbose=True)

# Query
response = agent.chat("What skills do I have for debugging?")
```

## AutoGen

```python
from autogen import AssistantAgent, UserProxyAgent
import requests

AISKILLS_URL = "http://localhost:8420"

# Function to be called by agents
def skill_search(query: str) -> str:
    response = requests.post(
        f"{AISKILLS_URL}/skills/search",
        json={"query": query}
    )
    return str(response.json()["results"])

def skill_read(name: str) -> str:
    response = requests.get(f"{AISKILLS_URL}/skills/{name}")
    return response.json()["content"]

# Register functions
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"},
    system_message="You can search and read AI skills."
)

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False
)

# Register functions
user_proxy.register_function(
    function_map={
        "skill_search": skill_search,
        "skill_read": skill_read,
    }
)

# Chat
user_proxy.initiate_chat(
    assistant,
    message="Find skills about testing APIs"
)
```

## Webhooks / Automation

### Zapier Integration

1. Create webhook trigger
2. Use HTTP action to call aiskills API
3. Process response in next step

### n8n Integration

```json
{
  "nodes": [
    {
      "name": "Search Skills",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8420/skills/search",
        "method": "POST",
        "bodyParameters": {
          "query": "={{ $json.query }}"
        }
      }
    }
  ]
}
```

## Deployment Options

### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install aiskills[api,search]
EXPOSE 8420
CMD ["aiskills", "api", "serve"]
```

### Docker Compose

```yaml
version: '3'
services:
  aiskills:
    build: .
    ports:
      - "8420:8420"
    volumes:
      - ./skills:/root/.aiskills/skills
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiskills
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: aiskills
        image: aiskills:latest
        ports:
        - containerPort: 8420
```

## Authentication (Production)

For production, add authentication:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403)
    return api_key

# Add to routes:
@app.get("/skills", dependencies=[Depends(verify_api_key)])
async def list_skills():
    ...
```

## Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/skills/search")
@limiter.limit("10/minute")
async def search_skills(request: Request, ...):
    ...
```
