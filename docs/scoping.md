# Declarative Scoping

aiskills supports **declarative scoping** that constrains when a skill is eligible for selection, reducing false positives from purely semantic matching.

## Overview

Scoping rules in the frontmatter define:
- **paths**: Glob patterns for file paths where skill applies
- **languages**: Programming languages/filetypes
- **triggers**: Hard keyword matches that strongly signal relevance
- **priority**: Numeric priority (0-100)
- **precedence**: Tier for override resolution

## Frontmatter Schema

```yaml
---
name: alembic-migrations
description: Guide for database migrations with Alembic
version: 1.0.0
tags: [python, database, migrations]

# Scoping configuration
scope:
  paths:
    - "src/db/**"
    - "migrations/**"
    - "alembic/**"
  languages:
    - python
  triggers:
    - migrate
    - alembic
    - revision
    - upgrade
    - downgrade

# Priority and precedence
priority: 75              # Higher = preferred (default: 50)
precedence: repository    # organization > repository > project > user > local
---
```

## How Scoping Works

### 1. Path Matching
When `active_paths` are provided, only skills whose `scope.paths` patterns match are eligible:

```yaml
scope:
  paths:
    - "src/api/**"      # Matches src/api/routes.py
    - "tests/**/*.py"   # Matches tests/unit/test_api.py
```

### 2. Language Matching
When `languages` context is provided or inferred from file extensions:

```yaml
scope:
  languages:
    - python
    - sql
```

Language detection from file extensions:
- `.py` → python
- `.ts`, `.tsx` → typescript
- `.rs` → rust
- `.go` → go
- etc.

### 3. Trigger Keywords
Hard keyword matches that boost the skill's score significantly:

```yaml
scope:
  triggers:
    - migrate
    - alembic
    - revision
```

If the user query contains "alembic", this skill gets a +0.3 bonus score.

### 4. Priority Scoring
Skills are sorted by combined score:

```
combined_score = (
    priority * 0.25 +           # Skill's priority (0-100)
    precedence_weight * 0.15 +  # organization=1.0, project=0.6, etc.
    scope_bonus * 0.20 +        # Trigger/path/language matches
    semantic_score * 0.40       # From embedding similarity
)
```

## Precedence Tiers

For multi-level configurations (org → team → project → user):

| Tier | Weight | Use Case |
|------|--------|----------|
| `organization` | 100 | Org-wide policies, standards |
| `repository` | 80 | Team/repo specific skills |
| `project` | 60 | Project-level customizations |
| `user` | 40 | User preferences |
| `local` | 20 | Local development overrides |

Example:
```yaml
precedence: repository   # This is a team-level skill
```

## Usage Examples

### API Request with Scope Context
```bash
curl -X POST http://localhost:8420/skills/use \
  -H "Content-Type: application/json" \
  -d '{
    "context": "help with database schema changes",
    "active_paths": ["src/db/models.py", "migrations/versions/"],
    "languages": ["python"]
  }'
```

### CLI with Scope Filters
```bash
# Filter by paths
aiskills browse --paths "src/api/**,tests/**"

# Filter by language
aiskills browse --lang python,sql

# Combined
aiskills browse "migration" --paths "migrations/**" --lang python
```

### Python SDK
```python
from aiskills.core.router import get_router
from aiskills.core.scoping import ScopeContext

router = get_router()

# Create scope context
result = router.use(
    context="set up CI/CD pipeline",
    active_paths=[".github/workflows/", "Dockerfile"],
    languages=["yaml"]
)
```

## Scope Matching Logic

1. If no scope constraints defined → skill matches everything
2. If constraints defined → ALL defined constraints must match:
   - `paths` defined → at least one path must match
   - `languages` defined → at least one language must match
   - `triggers` defined → at least one trigger must appear in query

## Best Practices

1. **Be specific with paths**: Use specific globs, not `**/*`
2. **Use triggers sparingly**: Only for strong domain signals
3. **Set appropriate priority**: Default 50, increase for specialized skills
4. **Consider precedence**: Org skills should override project skills

## Example: Multi-Scope Skill

```yaml
---
name: kubernetes-deployment
description: Kubernetes deployment patterns and troubleshooting
version: 1.0.0

scope:
  paths:
    - "k8s/**"
    - "kubernetes/**"
    - "deploy/**"
    - "**/deployment.yaml"
    - "**/service.yaml"
  languages:
    - yaml
  triggers:
    - kubectl
    - kubernetes
    - k8s
    - pod
    - deployment
    - service
    - ingress

priority: 70
precedence: repository
---
```

This skill will:
- Only compete when working with k8s-related paths
- Get bonus for YAML files
- Strongly match queries containing "kubectl", "kubernetes", etc.
