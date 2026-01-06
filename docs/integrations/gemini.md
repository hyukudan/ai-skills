# Google Gemini Integration

**Ai Skills** can power Google Gemini models by providing a dynamic toolset for knowledge retrieval. While there is no direct "plugin" system like MCP for Gemini yet, you can easily integrate Ai Skills using Gemini's **Function Calling** capabilities via the Python SDK.

## Overview

The integration works by:
1.  Defining Ai Skills tools (search, read) as Gemini Function Declarations.
2.  Allowing the Gemini model to "call" these tools when it needs information.
3.  Executing the tool locally using the `aiskills` SDK.
4.  Feeding the result back to Gemini.

## Setup

First, ensure you have the necessary packages:

```bash
pip install aiskills google-generativeai
```

## Python SDK Example

Here is a complete example of how to build a Gemini-powered agent with access to your skills.

```python
import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from aiskills import SkillManager

# 1. Initialize Ai Skills
skill_manager = SkillManager()

# 2. Define Tools Wrapper
def search_skills(query: str):
    """Search for relevant skills based on a query."""
    results = skill_manager.search(query, limit=3)
    return "\n".join([f"Skill: {r.skill.name}\nDescription: {r.skill.description}" for r in results])

def read_skill(name: str):
    """Read the full content of a specific skill."""
    try:
        skill = skill_manager.read_skill(name)
        return skill.content
    except Exception as e:
        return f"Error reading skill: {str(e)}"

# 3. Create Function Declarations
tools = [
    search_skills,
    read_skill
]

# 4. Initialize Gemini with Tools
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=tools
)

# 5. Start Chat
chat = model.start_chat(enable_automatic_function_calling=True)

# 6. Interacting
response = chat.send_message("I need to debug a memory leak in my Python app. Do we have any guides?")
print(response.text)
```

## How it Works

1.  **`search_skills`**: When you ask about "debugging", Gemini decides to call this function.
2.  **`aiskills` Execution**: The function searches your local markdown files.
3.  **Context Injection**: The search results (names and descriptions) are returned to Gemini.
4.  **`read_skill`**: If Gemini thinks a specific skill looks useful, it calls this function to get the full markdown content.
5.  **Final Answer**: Gemini uses the skill content to answer your question precisely.

## HTTP API Usage

If you are not using Python, you can run `aiskills api serve` and use the HTTP endpoints to fetch tool definitions compatible with the [OpenAI format](https://platform.openai.com/docs/guides/function-calling), which many Gemini wrappers libraries also support or can be adapted to.

```bash
aiskills api serve
# Endpoint: http://localhost:8420/openai/tools
```
