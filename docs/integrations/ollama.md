# Ollama & Local LLM Integration

**Ai Skills** is designed to work perfectly with local LLMs running via **Ollama**, **Llama.cpp**, or similar tools. Since local LLMs often have limited context windows, purely injecting *all* skills is impossible. Ai Skills solves this by dynamically retrieving only the relevant skills.

## Strategy

There are two main ways to use Ai Skills with Ollama:

1.  **CLI Pipe (Easiest)**: Pipe skill content directly into your Ollama prompt.
2.  **Python Wrapper**: Use a simple Python script to orchestrate the conversation.

## Method 1: CLI Pipelining

This is great for one-off queries where you know which skill you want, or want to search and pipe.

**Example: Search and Ask**
```bash
# 1. Search for a skill on "linux commands" and get the top result name
SKILL=$(aiskills search "linux networking" --limit 1 --name-only)

# 2. Read the skill and pipe it to ollama
aiskills read $SKILL | ollama run llama3 "How do I check open ports based on this guide?"
```

## Method 2: Python Agent (Recommended)

For a more interactive experience, you can create a small script that gives Ollama "tools".

### Prerequisites
```bash
pip install aiskills ollama
```

### Agent Script (`agent.py`)

```python
import ollama
from aiskills import SkillManager

manager = SkillManager()

# Define tools for Ollama (if model supports tool calling like Llama 3.1)
tools = [
    {
      'type': 'function',
      'function': {
        'name': 'search_skills',
        'description': 'Search for coding skills and guides',
        'parameters': {
          'type': 'object',
          'properties': {
            'query': {
              'type': 'string',
              'description': 'The search query',
            },
          },
          'required': ['query'],
        },
      },
    },
    {
      'type': 'function',
      'function': {
        'name': 'read_skill',
        'description': 'Read the content of a specific skill',
        'parameters': {
          'type': 'object',
          'properties': {
            'name': {
              'type': 'string',
              'description': 'The exact name of the skill',
            },
          },
          'required': ['name'],
        },
      },
    }
]

# Simple loop
messages = []

while True:
    user_input = input("You: ")
    messages.append({'role': 'user', 'content': user_input})

    response = ollama.chat(
        model='llama3.1',
        messages=messages,
        tools=tools,
    )
    
    # Check for tool calls
    if response['message'].get('tool_calls'):
        for tool in response['message']['tool_calls']:
            if tool['function']['name'] == 'search_skills':
                query = tool['function']['arguments']['query']
                print(f"Searching for: {query}...")
                results = manager.search(query)
                content = "\n".join([f"- {r.skill.name}: {r.skill.description}" for r in results])
                messages.append({'role': 'tool', 'content': content})
            
            elif tool['function']['name'] == 'read_skill':
                name = tool['function']['arguments']['name']
                print(f"Reading skill: {name}...")
                try:
                    skill = manager.read_skill(name)
                    messages.append({'role': 'tool', 'content': skill.content})
                except:
                    messages.append({'role': 'tool', 'content': "Skill not found."})

        # Get final response with tool outputs
        final_response = ollama.chat(model='llama3.1', messages=messages)
        print("Bot:", final_response['message']['content'])
        messages.append(final_response['message'])
    
    else:
        print("Bot:", response['message']['content'])
        messages.append(response['message'])
```

## Supported Models

-   **Llama 3.1 & 3.2**: Excellent tool calling support.
-   **Mistral**: Good instruction following, can use method 1 easily.
-   **Qwen**: Also supports tool calling in newer versions.
