# Security & Sandboxing

aiskills includes a **security policy system** for controlling access to skill resources, especially executable scripts.

## Overview

Each skill can define a security policy that controls:
- Which resource types can be accessed
- Whether scripts can be executed
- Specific commands that are allowed
- Sandbox strictness level

## Security Policy Schema

```yaml
---
name: deployment-automation
description: Automated deployment helpers

security:
  # Resource types this skill can access
  allowed_resources:
    - references      # Documentation, guides
    - templates       # Template files
    # - scripts       # Commented out = disabled
    # - assets        # Binary assets

  # Whether scripts can be executed
  allow_execution: false   # Default: false

  # Sandbox strictness
  sandbox_level: standard  # strict | standard | permissive

  # Specific commands/scripts allowed (if allow_execution: true)
  allowlist:
    - "lint.sh"
    - "validate.py"
---
```

## Resource Types

| Type | Directory | Default | Description |
|------|-----------|---------|-------------|
| `references` | `references/` | Allowed | Documentation, guides, checklists |
| `templates` | `templates/` | Allowed | Template files for generation |
| `scripts` | `scripts/` | Blocked | Executable scripts |
| `assets` | `assets/` | Blocked | Binary files, images |

## Execution Control

### Default: No Execution
```yaml
security:
  allow_execution: false  # Default
```

With execution disabled:
- Scripts in `scripts/` are listed but marked `allowed: false`
- API returns resource metadata but won't serve script content
- Provides provenance tracking (what skill tried to access what)

### Enabling Execution
```yaml
security:
  allow_execution: true
  allowlist:
    - "setup.sh"       # Only these scripts can run
    - "validate.py"
```

## Sandbox Levels

### Strict
```yaml
security:
  sandbox_level: strict
```
- Only `references/` accessible
- No execution under any circumstances
- For untrusted or third-party skills

### Standard (Default)
```yaml
security:
  sandbox_level: standard
```
- `references/` and `templates/` accessible
- Execution requires explicit `allow_execution: true`
- Allowlist enforced when execution enabled

### Permissive
```yaml
security:
  sandbox_level: permissive
```
- All resource types accessible
- Execution allowed with allowlist
- For trusted, internal skills only

## Resource Access via API

### List Resources (Phase 3 Preparation)
```bash
curl http://localhost:8420/skills/deployment-automation/resources
```

Response shows what's allowed:
```json
{
  "resources": [
    {
      "name": "deployment-guide.md",
      "resource_type": "reference",
      "allowed": true,
      "requires_execution": false
    },
    {
      "name": "deploy.sh",
      "resource_type": "script",
      "allowed": false,          # Blocked by policy
      "requires_execution": true
    }
  ]
}
```

### Load Resource
```bash
curl -X POST http://localhost:8420/skills/resource \
  -d '{"skill_name": "deployment-automation", "resource_name": "deploy.sh"}'
```

If blocked, returns 404 with security reason.

## Provenance Tracking

The system tracks resource access attempts:

```python
skill = manager.get("deployment-automation")
resources = skill.list_resources()

for r in resources:
    print(f"{r.name}: allowed={r.allowed}, exec={r.requires_execution}")
    # deploy.sh: allowed=False, exec=True
```

This enables:
- Audit logging of access attempts
- Security policy compliance checking
- Understanding what skills need

## Example Policies

### Documentation-Only Skill
```yaml
security:
  allowed_resources: [references]
  allow_execution: false
  sandbox_level: strict
```

### Template Generator
```yaml
security:
  allowed_resources: [references, templates]
  allow_execution: false
  sandbox_level: standard
```

### CI/CD Automation (Trusted)
```yaml
security:
  allowed_resources: [references, templates, scripts]
  allow_execution: true
  sandbox_level: permissive
  allowlist:
    - "deploy.sh"
    - "rollback.sh"
    - "health_check.py"
```

### Third-Party Skill (Untrusted)
```yaml
security:
  allowed_resources: [references]
  allow_execution: false
  sandbox_level: strict
```

## Local Override for Execution

Enable execution locally without modifying shared skill:

```yaml
# SKILL.local.md
---
security:
  allow_execution: true
  allowlist:
    - "internal_deploy.sh"
---
```

## Best Practices

1. **Default to strict**: Start with minimal permissions
2. **Use allowlists**: Never enable blanket execution
3. **Audit regularly**: Review what skills request
4. **Separate concerns**: Keep scripts in dedicated skills
5. **Trust hierarchy**: Use precedence for trust levels:
   - Organization skills: Can be permissive
   - Third-party: Always strict

## Integration with Agents

LLM agents should:
1. Check `allowed` field before requesting resources
2. Respect `requires_execution` warnings
3. Never execute scripts without explicit user approval
4. Log all resource access attempts

```python
# Agent code example
resources = router.list_resources(skill_name)

for resource in resources:
    if resource.requires_execution:
        # Require user confirmation
        if not user_approved(f"Execute {resource.name}?"):
            continue

    if resource.allowed:
        content = router.resource(skill_name, resource.name)
```
