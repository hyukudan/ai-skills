# Progressive Disclosure System

aiskills implements a formal **3-phase progressive disclosure** system that optimizes token usage and improves skill discovery accuracy.

## Overview

The system works in three phases:

```
Phase 1: BROWSE    →    Phase 2: LOAD    →    Phase 3: USE
(metadata only)        (full content)        (extra resources)
```

This allows LLM agents to:
1. Discover relevant skills without loading full content
2. Make informed decisions based on metadata (tokens, scope, priority)
3. Load additional resources on-demand

## Phase 1: Browse

**Purpose**: List available skills with lightweight metadata only.

### CLI
```bash
# Browse all skills
aiskills browse

# Semantic search
aiskills browse "debug python memory leak"

# Filter by scope
aiskills browse --paths "src/api/**" --lang python

# JSON output with full metadata
aiskills browse --json
```

### API
```bash
# POST /skills/browse
curl -X POST http://localhost:8420/skills/browse \
  -H "Content-Type: application/json" \
  -d '{
    "context": "debug python",
    "active_paths": ["src/api/routes.py"],
    "languages": ["python"],
    "limit": 10
  }'
```

### Response (SkillBrowseInfo)
```json
{
  "skills": [
    {
      "name": "python-debugging",
      "description": "Guide for debugging Python applications",
      "version": "1.0.0",
      "tags": ["python", "debugging"],
      "tokens_est": 1250,
      "priority": 50,
      "precedence": "project",
      "scope_paths": ["**/*.py"],
      "scope_languages": ["python"],
      "scope_triggers": ["debug", "error", "traceback"],
      "has_variables": true,
      "has_dependencies": false
    }
  ],
  "total": 1
}
```

## Phase 2: Load

**Purpose**: Load full skill content for the selected skill.

### CLI
```bash
aiskills use "debug python memory leak"
aiskills read python-debugging
```

### API
```bash
# POST /skills/use
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{
    "context": "debug python memory leak",
    "variables": {"framework": "django"},
    "active_paths": ["src/api/routes.py"],
    "languages": ["python"]
  }'
```

### Response (UseResponse)
```json
{
  "skill_name": "python-debugging",
  "content": "# Skill: python-debugging v1.0.0\n...",
  "score": 0.85,
  "matched_query": "debug python memory leak",
  "available_resources": ["checklist.md", "tools.sh"],
  "tokens_used": 1250
}
```

## Phase 3: Use (Resources)

**Purpose**: Load additional resources on-demand.

### List Available Resources
```bash
# GET /skills/{name}/resources
curl http://localhost:8420/skills/python-debugging/resources
```

### Response
```json
{
  "skill_name": "python-debugging",
  "resources": [
    {
      "resource_type": "reference",
      "name": "checklist.md",
      "size_bytes": 2048,
      "tokens_est": 512,
      "requires_execution": false,
      "allowed": true
    },
    {
      "resource_type": "script",
      "name": "profile.sh",
      "size_bytes": 1024,
      "tokens_est": 256,
      "requires_execution": true,
      "allowed": false
    }
  ]
}
```

### Load Specific Resource
```bash
# POST /skills/resource
curl -X POST http://localhost:8420/skills/resource \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "python-debugging",
    "resource_name": "checklist.md"
  }'
```

## Token Estimation

Each skill includes `tokens_est` (estimated tokens) calculated as:
- `content_length / 4 + 100` (overhead)

This allows agents to:
- Budget context window usage
- Choose lighter skills when appropriate
- Defer loading until necessary

## Integration Example

```python
from aiskills.core.router import get_router

router = get_router()

# Phase 1: Browse
candidates = router.browse(
    context="help with database migration",
    active_paths=["src/db/models.py"],
    languages=["python"],
    limit=5
)

# Inspect metadata before loading
for skill in candidates:
    print(f"{skill.name}: ~{skill.tokens_est} tokens")

# Phase 2: Load best match
result = router.use(
    context="help with database migration",
    active_paths=["src/db/models.py"]
)

print(result.content)
print(f"Available resources: {result.available_resources}")

# Phase 3: Load extra resource if needed
if "migration_template.sql" in result.available_resources:
    template = router.resource(
        result.skill_name,
        "migration_template.sql"
    )
    print(template)
```
