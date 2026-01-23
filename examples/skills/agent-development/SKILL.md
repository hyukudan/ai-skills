---
name: agent-development
description: |
  Patterns for building LLM-powered agents that can reason, plan, and use tools.
  Covers agent architectures (ReAct, Plan-and-Execute), tool design, multi-agent
  systems, memory management, and production deployment considerations.
license: MIT
allowed-tools: Read Edit Bash WebFetch
version: 1.0.0
tags: [ai, agents, llm, tools, langchain, autogen, crew-ai]
category: ai/agents
trigger_phrases:
  - "AI agent"
  - "LLM agent"
  - "tool use"
  - "function calling"
  - "ReAct"
  - "multi-agent"
  - "agentic"
  - "autonomous agent"
  - "agent loop"
variables:
  framework:
    type: string
    description: Agent framework
    enum: [langchain, autogen, custom, claude]
    default: custom
  complexity:
    type: string
    description: Agent complexity
    enum: [single, multi-agent, hierarchical]
    default: single
---

# Agent Development Guide

## Core Philosophy

**Agents are LLMs in a loop with tools.** The key is designing the right loop, the right tools, and the right stopping conditions.

> "An agent is only as good as its worst tool and its ability to know when to stop."

---

## Agent Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Agent Loop                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  Observe │───▶│  Think   │───▶│   Act    │──┐   │
│  └──────────┘    └──────────┘    └──────────┘  │   │
│       ▲                                         │   │
│       └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │                              │
         │                              ▼
    ┌────┴────┐                  ┌───────────┐
    │ Memory  │                  │   Tools   │
    └─────────┘                  └───────────┘
```

---

## 1. Agent Patterns

### ReAct (Reasoning + Acting)

The most common pattern. LLM reasons about what to do, takes action, observes result.

```python
REACT_PROMPT = """Answer the question using available tools.

Tools available:
{tools}

Use this format:
Thought: I need to figure out...
Action: tool_name
Action Input: input for the tool
Observation: tool result
... (repeat as needed)
Thought: I now know the answer
Final Answer: the answer

Question: {question}
"""

def react_agent(question: str, tools: dict, llm, max_steps: int = 10) -> str:
    """Simple ReAct agent implementation."""
    history = []

    for step in range(max_steps):
        # Generate next action
        prompt = REACT_PROMPT.format(
            tools=format_tools(tools),
            question=question
        ) + "\n".join(history)

        response = llm.generate(prompt)
        history.append(response)

        # Check for final answer
        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()

        # Parse and execute action
        action, action_input = parse_action(response)
        if action in tools:
            observation = tools[action](action_input)
            history.append(f"Observation: {observation}")
        else:
            history.append(f"Observation: Unknown tool '{action}'")

    return "Max steps reached without answer"
```

### Plan-and-Execute

Better for complex multi-step tasks. Plan first, then execute steps.

```python
def plan_and_execute(task: str, tools: dict, llm) -> str:
    """Plan first, then execute each step."""

    # Step 1: Create plan
    plan_prompt = f"""Create a step-by-step plan to accomplish this task.

    Available tools: {list(tools.keys())}

    Task: {task}

    Plan (numbered steps):"""

    plan = llm.generate(plan_prompt)
    steps = parse_plan(plan)

    # Step 2: Execute each step
    results = []
    for i, step in enumerate(steps):
        execute_prompt = f"""Execute this step of the plan.

        Previous results: {results}
        Current step: {step}

        What tool should I use and with what input?"""

        action = llm.generate(execute_prompt)
        tool_name, tool_input = parse_action(action)

        result = tools[tool_name](tool_input)
        results.append(f"Step {i+1}: {result}")

    # Step 3: Synthesize final answer
    return synthesize_answer(task, results, llm)
```

### Reflection Pattern

Agent critiques its own work and improves.

```python
def reflection_agent(task: str, llm, max_iterations: int = 3) -> str:
    """Generate, critique, and improve."""

    # Initial attempt
    response = llm.generate(f"Complete this task: {task}")

    for i in range(max_iterations):
        # Self-critique
        critique = llm.generate(f"""Review this response for errors or improvements:

        Task: {task}
        Response: {response}

        Critique (be specific about issues):""")

        # Check if good enough
        if "no issues" in critique.lower() or "looks good" in critique.lower():
            break

        # Improve based on critique
        response = llm.generate(f"""Improve this response based on the critique:

        Original: {response}
        Critique: {critique}

        Improved response:""")

    return response
```

---

## 2. Tool Design

### Tool Definition Pattern

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    function: Callable

    def to_schema(self) -> dict:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

# Example tool
search_tool = Tool(
    name="web_search",
    description="Search the web for current information. Use for recent events or facts you're unsure about.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        "required": ["query"]
    },
    function=lambda query: search_api(query)
)
```

### Tool Design Principles

| Principle | Good | Bad |
|-----------|------|-----|
| **Single purpose** | `get_weather(city)` | `get_weather_and_news(city)` |
| **Clear description** | "Search for current stock prices by ticker symbol" | "Search stuff" |
| **Obvious parameters** | `send_email(to, subject, body)` | `send_email(data)` |
| **Graceful errors** | Returns error message | Raises exception |

### Error Handling in Tools

```python
def safe_tool_wrapper(tool_fn: Callable) -> Callable:
    """Wrap tool to handle errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            result = tool_fn(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Try different parameters or use another tool"
            }
    return wrapper
```

---

## 3. Memory Systems

### Conversation Memory

```python
class ConversationMemory:
    """Simple sliding window memory."""

    def __init__(self, max_messages: int = 20):
        self.messages = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            # Keep system message + recent messages
            self.messages = self.messages[:1] + self.messages[-(self.max_messages-1):]

    def get_context(self) -> list:
        return self.messages.copy()
```

### Summary Memory

```python
class SummaryMemory:
    """Compress old context into summaries."""

    def __init__(self, llm, summary_threshold: int = 10):
        self.llm = llm
        self.summary = ""
        self.recent_messages = []
        self.threshold = summary_threshold

    def add(self, role: str, content: str):
        self.recent_messages.append({"role": role, "content": content})

        if len(self.recent_messages) > self.threshold:
            self._compress()

    def _compress(self):
        """Summarize older messages."""
        to_summarize = self.recent_messages[:-5]  # Keep last 5

        summary_prompt = f"""Summarize this conversation concisely:

        Previous summary: {self.summary}

        New messages:
        {format_messages(to_summarize)}

        Updated summary:"""

        self.summary = self.llm.generate(summary_prompt)
        self.recent_messages = self.recent_messages[-5:]

    def get_context(self) -> str:
        return f"Summary: {self.summary}\n\nRecent:\n{format_messages(self.recent_messages)}"
```

### Entity Memory

```python
class EntityMemory:
    """Track entities mentioned in conversation."""

    def __init__(self):
        self.entities = {}  # name -> {type, facts, last_mentioned}

    def extract_and_store(self, text: str, llm):
        """Extract entities from text."""
        prompt = f"""Extract entities from this text.
        Format: entity_name|entity_type|key_fact

        Text: {text}

        Entities:"""

        extracted = llm.generate(prompt)
        for line in extracted.strip().split('\n'):
            if '|' in line:
                name, etype, fact = line.split('|')
                if name not in self.entities:
                    self.entities[name] = {"type": etype, "facts": []}
                self.entities[name]["facts"].append(fact)

    def get_relevant(self, query: str) -> dict:
        """Get entities relevant to query."""
        # Simple keyword matching; could use embeddings
        relevant = {}
        query_lower = query.lower()
        for name, data in self.entities.items():
            if name.lower() in query_lower:
                relevant[name] = data
        return relevant
```

---

## 4. Multi-Agent Systems

{% if complexity == "multi-agent" or complexity == "hierarchical" %}

### Orchestrator Pattern

```python
class Orchestrator:
    """Coordinates multiple specialized agents."""

    def __init__(self, agents: dict, llm):
        self.agents = agents  # name -> agent
        self.llm = llm

    def route(self, task: str) -> str:
        """Route task to appropriate agent."""

        agent_descriptions = "\n".join([
            f"- {name}: {agent.description}"
            for name, agent in self.agents.items()
        ])

        routing_prompt = f"""Which agent should handle this task?

        Agents:
        {agent_descriptions}

        Task: {task}

        Best agent (name only):"""

        agent_name = self.llm.generate(routing_prompt).strip()

        if agent_name in self.agents:
            return self.agents[agent_name].run(task)
        else:
            return f"No suitable agent found for: {task}"
```

### Debate Pattern

```python
def debate_agents(question: str, agents: list, llm, rounds: int = 2) -> str:
    """Multiple agents debate to reach better answer."""

    # Initial answers
    answers = {}
    for agent in agents:
        answers[agent.name] = agent.run(question)

    # Debate rounds
    for round in range(rounds):
        for agent in agents:
            other_answers = {k: v for k, v in answers.items() if k != agent.name}

            debate_prompt = f"""Consider other perspectives and refine your answer.

            Question: {question}
            Your answer: {answers[agent.name]}

            Other perspectives:
            {format_dict(other_answers)}

            Refined answer:"""

            answers[agent.name] = agent.llm.generate(debate_prompt)

    # Synthesize final answer
    synthesis_prompt = f"""Synthesize the best answer from these perspectives:

    Question: {question}
    Perspectives: {format_dict(answers)}

    Best answer:"""

    return llm.generate(synthesis_prompt)
```

### Hierarchical Agents

```
┌─────────────────────────────────────┐
│          Manager Agent              │
│   (decomposes, delegates, merges)   │
└───────────┬───────────┬─────────────┘
            │           │
    ┌───────▼───┐   ┌───▼───────┐
    │  Research │   │  Writing  │
    │   Agent   │   │   Agent   │
    └───────────┘   └───────────┘
```

```python
class ManagerAgent:
    """Decomposes tasks and delegates to worker agents."""

    def __init__(self, workers: dict, llm):
        self.workers = workers
        self.llm = llm

    def run(self, task: str) -> str:
        # Decompose
        subtasks = self.decompose(task)

        # Delegate and collect
        results = {}
        for subtask in subtasks:
            worker = self.select_worker(subtask)
            results[subtask] = self.workers[worker].run(subtask)

        # Merge results
        return self.merge(task, results)

    def decompose(self, task: str) -> list:
        prompt = f"Break this task into 2-4 subtasks:\n\nTask: {task}\n\nSubtasks:"
        response = self.llm.generate(prompt)
        return [s.strip() for s in response.split('\n') if s.strip()]
```

{% endif %}

---

## 5. Stopping Conditions

### When to Stop

```python
class StoppingCondition:
    """Determine when agent should stop."""

    def __init__(self, max_steps: int = 20, max_tokens: int = 10000):
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.current_steps = 0
        self.current_tokens = 0

    def should_stop(self, response: str) -> tuple[bool, str]:
        self.current_steps += 1
        self.current_tokens += len(response.split())  # Rough estimate

        # Explicit completion
        if any(phrase in response.lower() for phrase in [
            "final answer:", "task complete", "i'm done"
        ]):
            return True, "completed"

        # Safety limits
        if self.current_steps >= self.max_steps:
            return True, "max_steps_reached"

        if self.current_tokens >= self.max_tokens:
            return True, "max_tokens_reached"

        # Stuck detection (same response repeated)
        # ... implement repetition detection

        return False, "continue"
```

---

## 6. Production Considerations

### Rate Limiting and Retries

```python
import time
from functools import wraps

def with_retry(max_retries: int = 3, backoff: float = 1.0):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    wait_time = backoff * (2 ** attempt)
                    time.sleep(wait_time)
            raise last_error
        return wrapper
    return decorator

@with_retry(max_retries=3)
def call_llm(prompt: str) -> str:
    return llm.generate(prompt)
```

### Logging and Observability

```python
import logging
from datetime import datetime

class AgentLogger:
    """Log agent actions for debugging and monitoring."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.trace = []

    def log_thought(self, thought: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "thought",
            "content": thought
        }
        self.trace.append(entry)
        self.logger.info(f"THOUGHT: {thought[:100]}...")

    def log_action(self, tool: str, input_data: any, output: any):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "action",
            "tool": tool,
            "input": input_data,
            "output": str(output)[:500]
        }
        self.trace.append(entry)
        self.logger.info(f"ACTION: {tool}({input_data}) -> {str(output)[:100]}")

    def get_trace(self) -> list:
        return self.trace
```

---

## Common Pitfalls

### 1. Infinite Loops

```python
# BAD: No exit condition
while True:
    response = agent.step()

# GOOD: Multiple exit conditions
for step in range(max_steps):
    response = agent.step()
    if is_complete(response) or is_stuck(response):
        break
```

### 2. Tool Overload

```python
# BAD: Too many similar tools
tools = [search_google, search_bing, search_duckduckgo, search_yahoo]

# GOOD: One clear tool per function
tools = [web_search, calculate, get_weather]
```

### 3. No Error Recovery

```python
# BAD: Crashes on tool error
result = tools[action](input)

# GOOD: Handle errors gracefully
try:
    result = tools[action](input)
except ToolError as e:
    result = f"Tool failed: {e}. Try a different approach."
    # Let agent adapt
```

---

## Quick Reference

### Choosing Agent Pattern

| Pattern | Best For | Complexity |
|---------|----------|------------|
| ReAct | Simple Q&A, single-step tasks | Low |
| Plan-Execute | Multi-step tasks, clear goals | Medium |
| Reflection | Quality-critical tasks | Medium |
| Multi-Agent | Complex domains, specialization | High |

### Tool Count Guidelines

| Agent Type | Recommended Tools |
|------------|-------------------|
| Simple assistant | 3-5 |
| Domain specialist | 5-10 |
| General agent | 10-15 max |

---

## Related Skills

- `rag-patterns` - Retrieval for agent knowledge
- `prompt-engineering` - Crafting agent prompts
- `llm-integration` - Connecting to LLM providers
