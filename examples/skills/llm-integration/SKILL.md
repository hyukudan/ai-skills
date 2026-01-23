---
name: llm-integration
version: 1.0.0
description: Guide for integrating AI Skills with any LLM provider - from local models to cloud APIs
license: MIT
allowed-tools: Read Edit Bash WebFetch
tags:
  - llm
  - integration
  - api
  - ollama
  - vllm
  - lmstudio
  - local-llm
  - openai
  - anthropic
  - gemini
category: integrations
author: AI Skills Team
trigger_phrases:
  - integrate with llm
  - use skills with ollama
  - connect to openai
  - llm provider setup
  - local model integration
  - function calling setup
variables:
  provider:
    type: string
    description: Target LLM provider
    enum:
      - ollama
      - openai
      - anthropic
      - gemini
      - generic
    default: generic
  integration_method:
    type: string
    description: How to integrate
    enum:
      - tool_calling
      - context_injection
      - rest_api
    default: tool_calling
  language:
    type: string
    description: Programming language
    enum:
      - python
      - typescript
      - curl
    default: python
---

# LLM Integration Guide

Integrate AI Skills with **{{ provider | capitalize }}** using **{{ integration_method | replace("_", " ") }}**.

## Overview

AI Skills is designed to be LLM-agnostic. This guide covers integration patterns for any provider.

### Integration Methods

| Method | Best For | Complexity |
|--------|----------|------------|
| Tool Calling | Full agentic workflows | Medium |
| Context Injection | Simple augmentation | Low |
| REST API | Any language/framework | Low |

---

{% if provider == "ollama" %}
## Ollama Integration

### Prerequisites
```bash
pip install aiskills ollama
```

{% if integration_method == "tool_calling" %}
### Tool Calling Setup

```python
import ollama
from aiskills.core.router import get_router

router = get_router()

# Define skill tools for Ollama
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'use_skill',
            'description': 'Find and use the best AI skill for a task',
            'parameters': {
                'type': 'object',
                'properties': {
                    'context': {
                        'type': 'string',
                        'description': 'What you need help with',
                    },
                },
                'required': ['context'],
            },
        },
    },
]

def handle_skill_call(args: dict) -> str:
    """Execute skill and return content."""
    result = router.use(context=args['context'])
    return f"**{result.skill_name}** (relevance: {result.score:.0%})\n\n{result.content}"

# Chat with tools
messages = [{'role': 'user', 'content': 'Help me debug a memory leak'}]
response = ollama.chat(
    model='llama3.1',
    messages=messages,
    tools=tools,
)

# Process tool calls
if response['message'].get('tool_calls'):
    for tool in response['message']['tool_calls']:
        result = handle_skill_call(tool['function']['arguments'])
        messages.append({'role': 'tool', 'content': result})

    # Get final response
    response = ollama.chat(model='llama3.1', messages=messages)

print(response['message']['content'])
```
{% elif integration_method == "context_injection" %}
### Context Injection

Inject skill content directly into prompts:

```python
from aiskills.core.router import get_router

router = get_router()

# Get relevant skill for context
result = router.use(context="debug python memory leak")
skill_content = result.content

# Inject into prompt
prompt = f"""You have access to this expert guide:

---
{skill_content}
---

User question: How do I find memory leaks in my Flask app?
"""

import ollama
response = ollama.generate(model='llama3.1', prompt=prompt)
print(response['response'])
```
{% else %}
### REST API Integration

```bash
# Start the API server
aiskills api serve --port 8420

# Use from any client
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{"context": "debug memory leak"}'
```
{% endif %}

{% elif provider == "openai" %}
## OpenAI Integration

### Prerequisites
```bash
pip install aiskills openai
```

{% if integration_method == "tool_calling" %}
### Function Calling Setup

```python
from openai import OpenAI
from aiskills.core.router import get_router

client = OpenAI()
router = get_router()

# Define tools in OpenAI format
tools = [
    {
        "type": "function",
        "function": {
            "name": "use_skill",
            "description": "Find and use the best AI skill for a coding task",
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Natural language description of what you need"
                    }
                },
                "required": ["context"]
            }
        }
    }
]

def process_tool_call(tool_call) -> str:
    args = json.loads(tool_call.function.arguments)
    result = router.use(context=args['context'])
    return result.content

messages = [{"role": "user", "content": "How do I optimize my SQL queries?"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = process_tool_call(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    # Get final response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

print(response.choices[0].message.content)
```
{% elif integration_method == "context_injection" %}
### Context Injection

```python
from openai import OpenAI
from aiskills.core.router import get_router

client = OpenAI()
router = get_router()

# Get skill content
result = router.use(context="optimize SQL queries")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": f"Use this expert guide:\n\n{result.content}"
        },
        {
            "role": "user",
            "content": "My SELECT query is slow with 1M rows"
        }
    ]
)

print(response.choices[0].message.content)
```
{% else %}
### REST API Integration

```bash
aiskills api serve

# OpenAI-compatible endpoint
curl http://localhost:8420/openai/tools
```
{% endif %}

{% elif provider == "anthropic" %}
## Anthropic (Claude) Integration

### Prerequisites
```bash
pip install aiskills anthropic
```

{% if integration_method == "tool_calling" %}
### Tool Use Setup

```python
import anthropic
from aiskills.core.router import get_router

client = anthropic.Anthropic()
router = get_router()

# Define tools for Claude
tools = [
    {
        "name": "use_skill",
        "description": "Find and use the best AI skill for a task",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "What you need help with"
                }
            },
            "required": ["context"]
        }
    }
]

def handle_tool_use(tool_use) -> str:
    result = router.use(context=tool_use.input['context'])
    return result.content

messages = [{"role": "user", "content": "Help me write better unit tests"}]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=tools,
    messages=messages
)

# Process tool use
while response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = handle_tool_use(block)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )

print(response.content[0].text)
```
{% elif integration_method == "context_injection" %}
### Context Injection

```python
import anthropic
from aiskills.core.router import get_router

client = anthropic.Anthropic()
router = get_router()

result = router.use(context="unit testing best practices")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=f"Expert guide available:\n\n{result.content}",
    messages=[
        {"role": "user", "content": "How should I test async functions?"}
    ]
)

print(response.content[0].text)
```
{% else %}
### MCP Integration (Recommended for Claude)

Add to Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aiskills": {
      "command": "aiskills",
      "args": ["mcp", "serve"]
    }
  }
}
```

This exposes skills as MCP tools that Claude can use natively.
{% endif %}

{% elif provider == "gemini" %}
## Google Gemini Integration

### Prerequisites
```bash
pip install aiskills google-generativeai
```

{% if integration_method == "tool_calling" %}
### Function Calling Setup

```python
import google.generativeai as genai
from aiskills.core.router import get_router

genai.configure(api_key="YOUR_API_KEY")
router = get_router()

def use_skill(context: str) -> str:
    """Find and use an AI skill for the given context."""
    result = router.use(context=context)
    return f"Skill: {result.skill_name}\n\n{result.content}"

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=[use_skill]
)

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("How do I profile Python performance?")
print(response.text)
```
{% elif integration_method == "context_injection" %}
### Context Injection

```python
import google.generativeai as genai
from aiskills.core.router import get_router

genai.configure(api_key="YOUR_API_KEY")
router = get_router()

result = router.use(context="python performance profiling")

model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(
    f"Guide:\n{result.content}\n\nQuestion: My function takes 5s, how to optimize?"
)
print(response.text)
```
{% else %}
### REST API

```bash
aiskills api serve
# Use /skills/use endpoint from any HTTP client
```
{% endif %}

{% else %}
## Generic Integration Pattern

This pattern works with any LLM that supports function/tool calling.

### Core Components

```python
from aiskills.core.router import get_router

router = get_router()

# 1. Define the tool schema (adapt to your LLM's format)
tool_schema = {
    "name": "use_skill",
    "description": "Find expert guidance for coding tasks",
    "parameters": {
        "context": {"type": "string", "required": True}
    }
}

# 2. Handle tool execution
def execute_skill_tool(context: str) -> str:
    result = router.use(context=context)
    return f"## {result.skill_name}\n\n{result.content}"

# 3. Integrate with your LLM's tool calling flow
# ... your LLM-specific code here ...
```

### Context Injection Pattern

```python
from aiskills.core.router import get_router

router = get_router()

def augment_prompt(user_query: str) -> str:
    """Augment user query with relevant skill content."""
    result = router.use(context=user_query)

    if result.score > 0.5:  # Only include if relevant
        return f"""Expert guidance available:

{result.content}

---

User question: {user_query}"""

    return user_query
```

### REST API (Language-Agnostic)

{% if language == "python" %}
```python
import requests

response = requests.post(
    "http://localhost:8420/skills/use",
    json={"context": "debug memory leak"}
)
skill_content = response.json()["content"]
```
{% elif language == "typescript" %}
```typescript
const response = await fetch('http://localhost:8420/skills/use', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ context: 'debug memory leak' })
});

const { content } = await response.json();
```
{% else %}
```bash
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{"context": "debug memory leak"}'
```
{% endif %}
{% endif %}

---

## System Prompt Template

Add to your LLM's system prompt for proactive skill usage:

```
You have access to AI Skills - expert coding guides.

When users ask about:
- Debugging, testing, or optimization
- Best practices or architecture
- Specific technologies or frameworks

ALWAYS call the use_skill tool first to get expert guidance.
Describe the task naturally: "debug python memory leak", "write unit tests".
```

## Best Practices

1. **Use tool calling** when building agents that need multiple skills per session
2. **Use context injection** for simple Q&A or single-turn interactions
3. **Cache skill lookups** for repeated queries (built-in with AI Skills)
4. **Set minimum score thresholds** to avoid low-relevance skills
5. **Combine with RAG** for domain-specific knowledge

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow first query | Embeddings are loaded lazily - first query is slower |
| No relevant skills | Lower min_score threshold or add custom skills |
| Tool not called | Strengthen system prompt instructions |
| Large skill content | Use variables to filter sections |
