# Local Overrides

aiskills supports **local override files** (`SKILL.local.md`) that allow customizing shared skills without modifying the original.

## Overview

When loading a skill, aiskills checks for `SKILL.local.md` in the same directory. If present, it merges the local overrides into the base skill.

```
my-skill/
├── SKILL.md           # Base skill (shared/versioned)
├── SKILL.local.md     # Local overrides (gitignored)
├── references/
└── templates/
```

## Use Cases

1. **Private configuration**: API keys, internal URLs, team conventions
2. **Environment-specific**: Different settings for dev/staging/prod
3. **Personal preferences**: Custom priority, additional tags
4. **Extended content**: Add team-specific sections

## Creating Local Overrides

### 1. Override Scalar Values

```yaml
# SKILL.local.md
---
name: python-debugging
priority: 90              # Boost priority locally
precedence: local         # Mark as local override
---
```

### 2. Extend Lists (Tags, Includes)

Lists are **extended**, not replaced:

```yaml
# SKILL.md
---
tags: [python, debugging]
---

# SKILL.local.md
---
tags: [internal, team-backend]   # Results in: [python, debugging, internal, team-backend]
---
```

### 3. Override Nested Objects

Nested objects (scope, security, variables) are **deep merged**:

```yaml
# SKILL.md
---
scope:
  paths: ["src/**"]
  languages: [python]
---

# SKILL.local.md
---
scope:
  paths: ["internal/api/**"]     # Added to paths
  triggers: [internal-api]       # Added trigger
---
```

### 4. Add Local Content

Content in SKILL.local.md is **appended** to the base:

```markdown
# SKILL.local.md
---
name: python-debugging
---

## Internal Resources

- Internal debugging dashboard: https://internal.example.com/debug
- Team Slack channel: #backend-debugging
- On-call runbook: https://wiki.internal/runbooks/debugging
```

## Merge Rules

| Field Type | Behavior |
|------------|----------|
| Scalar (string, int, bool) | Override |
| List | Extend (unique values) |
| Dict/Object | Deep merge |
| Content (markdown) | Append |

## Precedence Auto-Update

When local overrides are applied, the skill's `precedence` is automatically set to `local`, giving it the lowest tier weight in priority calculations.

## Gitignore Pattern

Add to `.gitignore` to keep local overrides private:

```gitignore
# Local skill overrides
**/SKILL.local.md
```

## Example: Full Override

```yaml
# SKILL.local.md for python-debugging
---
name: python-debugging

# Boost for internal use
priority: 85

# Add internal scopes
scope:
  paths:
    - "internal/services/**"
  triggers:
    - sentry
    - datadog

# Internal variables
variables:
  sentry_dsn:
    type: string
    default: "https://key@sentry.internal.io/123"
  log_endpoint:
    type: string
    default: "https://logs.internal.example.com"

# Security: allow internal scripts
security:
  allow_execution: true
  allowlist:
    - "debug_helper.sh"
    - "fetch_logs.py"
---

## Internal Debugging Tools

### Sentry Integration
Configure with: `{{ sentry_dsn }}`

### Log Aggregation
Fetch logs: `curl {{ log_endpoint }}/api/logs?service=myapp`

### Team Contacts
- Backend: @backend-team
- SRE: @sre-oncall
```

## Loading Behavior

```python
from aiskills.core.loader import get_loader

loader = get_loader()

# Load with local overrides (default)
skill = loader.load("skills/python-debugging")
print(skill.manifest.priority)  # 85 (from local)

# Load without local overrides
skill_base = loader.load(
    "skills/python-debugging",
    apply_local_overrides=False
)
print(skill_base.manifest.priority)  # 50 (original)
```

## API Behavior

The API always applies local overrides when loading skills. The response includes merged content without distinguishing base vs. local.

## Best Practices

1. **Keep SKILL.local.md small**: Only override what's needed
2. **Don't duplicate content**: Use for additions, not copies
3. **Document internal changes**: Add comments in local file
4. **Use for secrets**: Put API keys in local, not base
5. **Gitignore consistently**: Ensure team uses same pattern
