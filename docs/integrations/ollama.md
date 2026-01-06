# Ollama & Local LLM Integration

**Ai Skills** is designed to work perfectly with local LLMs running via **Ollama**, **Llama.cpp**, or similar tools. Since local LLMs often have limited context windows, purely injecting *all* skills is impossible. Ai Skills solves this by dynamically retrieving only the relevant skills.

## Strategy

There are three main ways to use Ai Skills with Ollama:

1.  **CLI Pipe (Easiest)**: Pipe skill content directly into your Ollama prompt.
2.  **Python Agent**: Use a Python script to orchestrate with tool calling.
3.  **REST API**: Connect via HTTP for any language/framework.

## Method 1: CLI Pipelining

This is great for one-off queries where you know which skill you want.

**Example: Use skill directly**
```bash
# Find and use the best skill for your task
aiskills use "debug python memory leak" | ollama run llama3 "Apply this to my code"

# Or search and read specific skills
SKILL=$(aiskills search "linux networking" --limit 1 --name-only)
aiskills read $SKILL | ollama run llama3 "How do I check open ports?"
```

## Method 2: Python Agent (Recommended)

For a more interactive experience, use the Ollama Python SDK with AI Skills tools.

### Prerequisites
```bash
pip install aiskills ollama
```

### Agent Script (`agent.py`)

```python
import ollama
from aiskills.core.router import get_router

router = get_router()

# System prompt that enables proactive skill usage
SYSTEM_PROMPT = """You have access to AI Skills - a library of expert coding knowledge.

Available tools:
- use_skill: Find the best skill for a task. Describe what you need.

IMPORTANT: When users ask about coding, debugging, or best practices,
ALWAYS call use_skill first to get expert guidance before answering.

Example: If user asks "help me with Python memory leaks", 
call use_skill with context="debug python memory leak" first."""

# Define tools for Ollama
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'use_skill',
            'description': 'Find and use the best AI skill for a task. Returns expert guidance.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'context': {
                        'type': 'string',
                        'description': 'Natural language description of what you need help with',
                    },
                },
                'required': ['context'],
            },
        },
    },
]

def handle_tool_call(tool_call):
    """Handle tool calls from the model."""
    name = tool_call['function']['name']
    args = tool_call['function']['arguments']
    
    if name == 'use_skill':
        result = router.use(context=args['context'])
        return f"**Skill: {result.skill_name}** (score: {result.score:.0%})\n\n{result.content}"
    
    return "Unknown tool"

# Simple chat loop
messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
        
    messages.append({'role': 'user', 'content': user_input})

    response = ollama.chat(
        model='llama3.1',
        messages=messages,
        tools=tools,
    )
    
    # Handle tool calls
    if response['message'].get('tool_calls'):
        for tool in response['message']['tool_calls']:
            print(f"🔍 Using skill for: {tool['function']['arguments'].get('context', '...')}")
            result = handle_tool_call(tool)
            messages.append({'role': 'tool', 'content': result})

        # Get final response with tool outputs
        response = ollama.chat(model='llama3.1', messages=messages)
    
    print("Bot:", response['message']['content'])
    messages.append(response['message'])
```

## Method 3: REST API

For any language, use the REST API:

```bash
# Start the server
aiskills api serve

# Use skill via HTTP
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{"context": "optimize SQL queries"}'
```

## System Prompt Template

Add this to your LLM's system prompt to enable proactive skill usage:

```
You have access to AI Skills via the use_skill tool. These are expert-crafted
guides for coding tasks.

GUIDELINES:
1. When users ask about coding, debugging, or optimization - CALL use_skill FIRST
2. Describe the task naturally: "debug python memory leak", "write unit tests"
3. Apply the skill's guidance to the user's specific problem
4. Mention which skill you used for transparency
```

## Supported Models

-   **Llama 3.1 & 3.2**: Excellent tool calling support.
-   **Mistral**: Good instruction following.
-   **Qwen 2.5**: Strong tool calling in newer versions.
-   **DeepSeek**: Works well with function calling.

