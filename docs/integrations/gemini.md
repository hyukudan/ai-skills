# Google Gemini Integration

This guide explains how to use aiskills with Google Gemini models.

## Option 1: REST API

Use the aiskills REST API with Gemini's function calling.

### Setup

1. **Start the API server:**
```bash
aiskills api serve
```

2. **Get tool definitions:**
```bash
curl http://localhost:8420/openai/tools
```

### Function Calling with Gemini

```python
import google.generativeai as genai
import requests
import json

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")

# Define tools in Gemini format
tools = [
    {
        "function_declarations": [
            {
                "name": "skill_search",
                "description": "Search for AI skills by query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "skill_read",
                "description": "Read a skill by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Skill name"
                        }
                    },
                    "required": ["name"]
                }
            }
        ]
    }
]

# Create model with tools
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=tools
)

chat = model.start_chat()
response = chat.send_message("How do I debug Python applications?")

# Handle function calls
for part in response.parts:
    if hasattr(part, "function_call"):
        func_name = part.function_call.name
        func_args = dict(part.function_call.args)

        # Call aiskills API
        result = requests.post(
            "http://localhost:8420/openai/call",
            json={"name": func_name, "arguments": func_args}
        )

        # Send result back to Gemini
        response = chat.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=func_name,
                        response={"result": result.json()}
                    )
                )]
            )
        )
```

## Option 2: AI Studio Integration

Use aiskills with Google AI Studio.

### Export Skills as Context

```python
import requests

# Get all skills
skills = requests.get("http://localhost:8420/skills").json()

# Create context string
context = "You have access to these skills:\n\n"
for skill in skills["skills"]:
    context += f"- {skill['name']}: {skill['description']}\n"

# Use in AI Studio prompt
system_prompt = f"""
{context}

When asked about coding topics, reference these skills and their guidance.
"""
```

### Manual Integration

1. Export skill content:
```bash
aiskills read python-debugging > skill_context.txt
```

2. Include in your AI Studio prompt as context

## Option 3: Vertex AI

For enterprise use with Vertex AI:

```python
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
import requests

# Define tools
skill_search = FunctionDeclaration(
    name="skill_search",
    description="Search for AI skills",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
        },
        "required": ["query"]
    }
)

skill_read = FunctionDeclaration(
    name="skill_read",
    description="Read a skill",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Skill name"},
        },
        "required": ["name"]
    }
)

tools = Tool(function_declarations=[skill_search, skill_read])

# Create model
model = GenerativeModel("gemini-1.5-pro", tools=[tools])

# Use in conversation
response = model.generate_content(
    "Help me with Python debugging",
    tools=[tools]
)

# Handle function calls
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.function_call:
            name = part.function_call.name
            args = dict(part.function_call.args)

            # Call aiskills
            result = requests.post(
                "http://localhost:8420/openai/call",
                json={"name": name, "arguments": args}
            ).json()
```

## Deployment for Gemini

### Cloud Run

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install aiskills[api,search]

# Copy your skills
COPY .aiskills /root/.aiskills

# Index skills
RUN aiskills search-index index

EXPOSE 8080
CMD ["aiskills", "api", "serve", "--port", "8080"]
```

Deploy:
```bash
gcloud run deploy aiskills --source . --allow-unauthenticated
```

### App Engine

```yaml
# app.yaml
runtime: python311

entrypoint: aiskills api serve --port $PORT

env_variables:
  AISKILLS_HOME: /tmp/aiskills
```

## Best Practices

1. **Pre-index skills** in your deployment
2. **Use caching** for frequently accessed skills
3. **Handle rate limits** gracefully
4. **Log function calls** for debugging

## Example: Complete Flow

```python
import google.generativeai as genai
import requests

AISKILLS_URL = "http://localhost:8420"

def call_skill_function(name: str, args: dict) -> dict:
    """Call an aiskills function."""
    response = requests.post(
        f"{AISKILLS_URL}/openai/call",
        json={"name": name, "arguments": args}
    )
    return response.json()

def chat_with_skills(user_message: str):
    """Chat with Gemini using aiskills."""
    # First, suggest relevant skills
    suggestions = requests.post(
        f"{AISKILLS_URL}/skills/suggest",
        json={"context": user_message, "limit": 3}
    ).json()

    # Build context
    context = "Relevant skills:\n"
    for s in suggestions["suggestions"]:
        skill = s["skill"]
        context += f"- {skill['name']}: {skill['description']}\n"

    # Chat with Gemini
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(f"{context}\n\nUser: {user_message}")

    return response.text

# Usage
result = chat_with_skills("How do I debug async Python code?")
print(result)
```
