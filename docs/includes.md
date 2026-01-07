# Includes & Composition

aiskills supports **skill composition** through includes, allowing reuse of content without duplication.

## Include Methods

### 1. Frontmatter Includes

List skills to include in the frontmatter:

```yaml
---
name: full-debugging-guide
description: Complete debugging guide

includes:
  - python-debugging@^1.0.0
  - logging-best-practices@>=2.0.0
---

# Full Debugging Guide

This guide combines multiple specialized skills.

{{> skill:python-debugging }}

## Logging

{{> skill:logging-best-practices }}
```

### 2. @include Directive

Use `@include` directly in content:

```markdown
# My Guide

## Python Debugging
@include python-debugging

## Common Patterns
@include snippets/debug-patterns.md
```

## Include Types

### Skill Include
```markdown
@include skill:python-debugging
# or simply
@include python-debugging
```

Includes the full rendered content of another skill.

### Snippet Include
```markdown
@include snippets/common-patterns.md
```

Includes a markdown file from:
- Current directory
- `.aiskills/snippets/`
- `.claude/snippets/`

## Depth Limit

Includes are limited to **5 levels deep** to prevent infinite loops:

```
skill-a
  └── includes skill-b (depth 1)
        └── includes skill-c (depth 2)
              └── includes skill-d (depth 3)
                    └── includes skill-e (depth 4)
                          └── includes skill-f (depth 5)
                                └── MAX DEPTH - stops here
```

At max depth, a warning comment is inserted instead of content.

## Cycle Detection

Circular includes are detected and prevented:

```yaml
# skill-a
includes:
  - skill-b

# skill-b
includes:
  - skill-a  # ERROR: Circular include detected
```

Result:
```markdown
<!-- ERROR: Circular include detected for skill-a -->
```

## Version Constraints

Includes support version constraints:

```yaml
includes:
  - base-skill@1.0.0      # Exact version
  - helper-skill@^2.0.0   # Compatible (>=2.0.0, <3.0.0)
  - util-skill@>=1.5.0    # Minimum version
```

## Extends vs Includes

### Extends (Inheritance)
```yaml
extends: base-skill@1.0.0
```
- Single parent only
- Base content comes first
- Child content appended with separator

### Includes (Composition)
```yaml
includes:
  - helper-a
  - helper-b
```
- Multiple includes allowed
- Content inserted at marker location
- More flexible placement

## Example: Composable Debugging Guide

### Base Skill (debugging-basics)
```yaml
---
name: debugging-basics
version: 1.0.0
---

## Core Debugging Principles

1. Reproduce the issue
2. Isolate the cause
3. Fix and verify
4. Prevent regression
```

### Python Extension
```yaml
---
name: python-debugging
version: 1.0.0
extends: debugging-basics@1.0.0
includes:
  - logging-patterns@^1.0.0
---

## Python-Specific Debugging

### Using pdb
...

## Logging
{{> skill:logging-patterns }}
```

### Result
The composed skill contains:
1. Base debugging principles (from extends)
2. Python-specific content
3. Logging patterns (from includes)

## Snippet Organization

Create reusable snippets:

```
.aiskills/
├── skills/
│   └── my-skill/
└── snippets/
    ├── common-headers.md
    ├── security-warnings.md
    └── team-contacts.md
```

Use in any skill:
```markdown
@include common-headers.md

# My Skill Content

@include security-warnings.md
```

## Recursive Resolution

Included content is fully resolved:
- Variables are rendered
- Nested includes are expanded
- @include directives are processed

```markdown
# Main skill
@include section-a

# section-a.md
Some content
@include subsection-a1

# subsection-a1.md
More content with {{ variable }}
```

All resolves to final combined output.

## Best Practices

1. **Keep includes focused**: Small, single-purpose snippets
2. **Version your includes**: Use constraints for stability
3. **Avoid deep nesting**: 2-3 levels is usually enough
4. **Document dependencies**: Note what gets included
5. **Test composition**: Verify rendered output

## Debugging Composition

Check what a skill includes:

```bash
# See raw content (shows include markers)
aiskills read my-skill --raw

# See resolved content (includes expanded)
aiskills read my-skill
```

Or via API:
```bash
# Raw
curl "http://localhost:8420/skills/my-skill?raw=true"

# Resolved
curl "http://localhost:8420/skills/my-skill"
```
