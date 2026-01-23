---
name: aiskills-guide
version: 2.0.0
description: |
  Decision frameworks for using AI Skills effectively. When to invoke skills,
  how to compose them, and integration patterns.
license: MIT
allowed-tools: Read Edit
tags: [meta, guide, skills, llm]
category: meta
variables:
  integration_type:
    type: string
    description: How you're integrating AI Skills
    enum: [cli, api, mcp, sdk]
    default: cli
scope:
  triggers:
    - how to use skills
    - which skill
    - skill workflow
    - combine skills
---

# AI Skills Guide

You help decide when and how to use skills effectively.

## When to Use Skills

```
SKILL DECISION:

Task type?
├── Best practices/patterns → Use skill
├── Architecture decisions → Use skill
├── Debugging complex issue → Use skill
├── Security review → Use skill
├── Simple factual question → Skip skill (LLM knows)
└── Trivial code fix → Skip skill

Skill exists for this domain?
├── Yes, good match → Use it
├── Partial match → Use with context
└── No match → LLM without skill
```

| Use Skill | Skip Skill |
|-----------|------------|
| "Design API authentication" | "What is REST?" |
| "Debug memory leak" | "Fix this typo" |
| "Set up CI/CD pipeline" | "Run npm install" |
| "Review security posture" | "What port does HTTP use?" |

---

## Search Mode Selection

```
SEARCH MODE DECISION:

Query type?
├── Natural language ("help me optimize queries") → Semantic (default)
├── Specific terms ("kubernetes yaml") → Hybrid (--hybrid)
└── Exact match needed ("redis") → Text (--text)

Getting wrong results?
├── Too broad → Add specifics or use hybrid
├── Too narrow → Use semantic search
└── Missing skill → Check aiskills list
```

{% if integration_type == "cli" %}
## CLI Usage

```bash
# Find relevant skills
aiskills search "performance bottleneck"
aiskills search "kubernetes deployment" --hybrid

# Use skill with variables
aiskills use "debug python" --var issue_type=memory_leak

# Check available variables
aiskills vars python-debugging

# List all skills
aiskills list
```

{% elif integration_type == "api" %}
## REST API Usage

```bash
# Search
curl -X POST localhost:8000/skills/search \
  -d '{"query": "debug python", "limit": 5}'

# Use
curl -X POST localhost:8000/skills/use \
  -d '{"context": "debug memory leak", "variables": {"issue_type": "memory_leak"}}'
```

{% elif integration_type == "mcp" %}
## MCP Integration

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "ai-skills": {
      "command": "aiskills",
      "args": ["mcp", "serve"]
    }
  }
}
```

**Available tools:** `skill_search`, `use_skill`, `skill_list`, `skill_read`

{% elif integration_type == "sdk" %}
## SDK Usage

```python
from aiskills import SkillRouter

router = SkillRouter()

# Search
results = router.search("python debugging", limit=5)

# Use with variables
result = router.use(
    context="debug memory leak",
    variables={"issue_type": "memory_leak"}
)
```

{% endif %}

---

## Skill Composition

### When to Combine Skills

```
COMPOSITION DECISION:

Task complexity?
├── Single domain → One skill
├── Multi-domain → Sequence of skills
└── Iterative → Same skill with different variables

Example sequences:
├── New feature: architecture → api-design → testing → security
├── Production issue: incident-response → debugging → logging
└── Code review: security → performance → code-review
```

### Composition Patterns

| Pattern | Use When | Example |
|---------|----------|---------|
| Sequential | Build on previous output | Design → Implement → Test |
| Parallel | Independent concerns | Security + Performance review |
| Conditional | Different paths | Error type → specific debug skill |
| Iterative | Refine approach | Same skill, adjusted variables |

---

## Variables

Skills have variables that customize output. Always check them.

{% if integration_type == "cli" %}
```bash
aiskills vars <skill-name>
```
{% elif integration_type == "sdk" %}
```python
skill = router.read("skill-name")
print(skill.variables)
```
{% endif %}

**Common variable patterns:**

| Variable | Affects | Example |
|----------|---------|---------|
| `language` | Code examples | python, typescript |
| `focus` | Content depth | specific area |
| `level` | Complexity | beginner, advanced |
| `context` | Environment | local, production |

---

## LLM Integration Patterns

### Tool-Based (OpenAI, Anthropic)

Define `use_skill` as a tool the LLM can call:
- LLM decides when to use skill based on query
- Skill content returned as tool result
- LLM applies guidance to specific code

### Context Injection (Local LLMs)

Prepend skill content to prompt:
- Search for relevant skill
- If score > threshold, include content
- LLM uses guidance in response

### When to Cache Skills

| Scenario | Cache? | Why |
|----------|--------|-----|
| Same query repeated | Yes | Avoid redundant search |
| Interactive session | Session | Variables may change |
| Production API | Yes | Reduce latency |
| Development | No | See fresh content |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| No skills found | Not installed | `aiskills list` |
| Wrong skill matched | Vague query | Be specific, use --hybrid |
| Low relevance score | Query mismatch | Rephrase, check categories |
| Variables not applied | Wrong names | `aiskills vars <skill>` |

---

## Best Practices

**DO:**
- Check skill variables before using
- Combine skills for complex tasks
- Be specific in search queries
- Adapt guidance to your context

**DON'T:**
- Use skills for trivial questions
- Apply advice blindly
- Ignore variable customization
- Skip skills for "known" topics

---

## Related Skills

- `skill-creator` - How to write effective skills
