---
name: skill-creator
description: |
  Guide for creating AI Skills in the ai-skills format. Use when building new skills,
  understanding the SKILL.md structure, or implementing variable-driven content.
  Covers YAML frontmatter, Jinja2 templating, and skill design best practices.
version: 1.0.0
tags: [ai-skills, skill-creation, meta, templating, jinja2]
category: meta/skill-development
variables:
  skill_complexity:
    type: string
    description: Complexity level of the skill to create
    enum: [simple, intermediate, advanced]
    default: intermediate
  content_type:
    type: string
    description: Type of content the skill provides
    enum: [guide, reference, tutorial, checklist]
    default: guide
---

# AI Skills Creation Guide

## What is a Skill?

A **Skill** is a structured knowledge document that provides context-aware guidance to AI assistants. Skills use:

- **YAML frontmatter** for metadata and configuration
- **Variables** for dynamic, context-specific content
- **Jinja2 templating** for conditional rendering
- **Markdown** for readable, structured content

> "A skill is a reusable piece of expertise that adapts to the specific context of each use."

---

## Skill Structure

### Directory Layout

```
skills/
└── my-skill/
    └── SKILL.md       # Required: The skill definition
```

### SKILL.md Anatomy

```markdown
---
name: skill-name
description: |
  Multi-line description of what this skill does.
  When to use it. What it covers.
version: 1.0.0
tags: [tag1, tag2, tag3]
category: domain/subdomain
variables:
  variable_name:
    type: string
    description: What this variable controls
    enum: [option1, option2, option3]
    default: option1
---

# Skill Title

Content goes here...

{% if variable_name == "option1" %}
## Conditional Section

This only appears when variable_name is "option1".
{% endif %}
```

---

## YAML Frontmatter Reference

### Required Fields

```yaml
---
name: my-skill                    # Unique identifier (kebab-case)
description: |                    # Multi-line description
  What this skill does.
  When to use it.
version: 1.0.0                   # Semantic versioning
---
```

### Optional Fields

```yaml
---
tags: [python, testing, quality]  # For search and categorization
category: development/testing     # Hierarchical category
author: Your Name                 # Skill author
license: MIT                      # License (if applicable)
---
```

### Variable Definitions

```yaml
variables:
  # String with enum (dropdown)
  language:
    type: string
    description: Programming language
    enum: [python, javascript, go, rust]
    default: python

  # String without enum (free text)
  project_name:
    type: string
    description: Name of the project
    default: my-project

  # Boolean (toggle)
  include_tests:
    type: boolean
    description: Include testing section
    default: true

  # Number
  max_items:
    type: number
    description: Maximum items to show
    default: 10
```

---

## Jinja2 Templating

### Conditional Content

```markdown
{% if language == "python" %}
## Python Implementation

​```python
def hello():
    print("Hello from Python!")
​```
{% elif language == "javascript" %}
## JavaScript Implementation

​```javascript
function hello() {
  console.log("Hello from JavaScript!");
}
​```
{% endif %}
```

### Multiple Conditions

```markdown
{% if language == "python" and include_tests %}
## Python with Tests

​```python
import pytest

def test_hello():
    assert hello() == "Hello"
​```
{% endif %}
```

### Loops (for lists)

```markdown
{% for item in items %}
- {{ item }}
{% endfor %}
```

### Variable Interpolation

```markdown
# {{ project_name }} Documentation

This guide covers {{ project_name }} setup for {{ language }}.
```

### Filters

```markdown
# {{ project_name | upper }}           → MY-PROJECT
# {{ project_name | title }}           → My-Project
# {{ description | truncate(100) }}    → First 100 chars...
```

---

{% if skill_complexity == "simple" %}
## Simple Skill Example

A simple skill has no variables—static content for a specific use case.

```markdown
---
name: commit-message-guide
description: |
  Best practices for writing git commit messages.
  Use when making commits or reviewing commit history.
version: 1.0.0
tags: [git, commits, best-practices]
category: development/git
---

# Commit Message Guide

## Format

​```
<type>(<scope>): <subject>

<body>
​```

## Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code restructuring

## Examples

​```
feat(auth): add OAuth2 login support

Implement Google and GitHub OAuth2 providers.
Closes #123
​```
```

{% elif skill_complexity == "intermediate" %}
## Intermediate Skill Example

An intermediate skill uses variables to adapt content to different contexts.

```markdown
---
name: api-client-guide
description: |
  Guide for building API clients. Adapts to language and HTTP library.
version: 1.0.0
tags: [api, http, client]
category: development/networking
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, go]
    default: python
  http_library:
    type: string
    description: HTTP library to use
    enum: [native, popular]
    default: popular
---

# API Client Guide

## Making HTTP Requests

{% if language == "python" %}
{% if http_library == "native" %}
### Using urllib (Native)

​```python
import urllib.request
import json

def get_user(user_id: str) -> dict:
    url = f"https://api.example.com/users/{user_id}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())
​```
{% else %}
### Using httpx (Recommended)

​```python
import httpx

async def get_user(user_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()
​```
{% endif %}
{% elif language == "javascript" %}
{% if http_library == "native" %}
### Using fetch (Native)

​```javascript
async function getUser(userId) {
  const response = await fetch(`https://api.example.com/users/${userId}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
​```
{% else %}
### Using axios (Popular)

​```javascript
import axios from 'axios';

async function getUser(userId) {
  const { data } = await axios.get(`https://api.example.com/users/${userId}`);
  return data;
}
​```
{% endif %}
{% endif %}
```

{% elif skill_complexity == "advanced" %}
## Advanced Skill Example

An advanced skill combines multiple variables with deep conditional logic.

```markdown
---
name: application-architecture
description: |
  Architecture patterns and project structure guide.
  Adapts to language, framework, and project scale.
version: 1.0.0
tags: [architecture, patterns, structure]
category: development/architecture
variables:
  language:
    type: string
    enum: [python, typescript, go]
    default: python
  framework:
    type: string
    enum: [fastapi, express, gin, none]
    default: fastapi
  scale:
    type: string
    enum: [small, medium, large]
    default: medium
  include_testing:
    type: boolean
    default: true
---

# Application Architecture Guide

{% if scale == "small" %}
## Simple Structure (Small Projects)

​```
src/
├── main.py          # Entry point + routes
├── models.py        # Data models
├── database.py      # DB connection
└── utils.py         # Helpers
​```
{% elif scale == "medium" %}
## Layered Structure (Medium Projects)

​```
src/
├── api/
│   ├── routes/      # HTTP handlers
│   └── middleware/  # Request processing
├── core/
│   ├── models/      # Domain models
│   └── services/    # Business logic
├── infrastructure/
│   ├── database/    # DB adapters
│   └── external/    # External services
└── main.py
​```
{% else %}
## Domain-Driven Structure (Large Projects)

​```
src/
├── domains/
│   ├── users/
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   └── orders/
│       ├── api/
│       ├── application/
│       ├── domain/
│       └── infrastructure/
├── shared/
│   ├── kernel/      # Shared domain concepts
│   └── infrastructure/
└── main.py
​```
{% endif %}

{% if language == "python" and framework == "fastapi" %}
## FastAPI Setup

​```python
from fastapi import FastAPI, Depends
from .api.routes import router
from .core.dependencies import get_db

app = FastAPI(title="My API")
app.include_router(router)
​```
{% endif %}

{% if include_testing %}
## Testing Structure

​```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
{% if scale == "large" %}
├── e2e/            # Full system tests
{% endif %}
└── conftest.py     # Shared fixtures
​```
{% endif %}
```

{% endif %}

---

{% if content_type == "guide" %}
## Writing Effective Guides

### Structure Pattern

```markdown
# Topic Name

## Philosophy / Why This Matters
Brief context on importance.

## Core Concepts
Key ideas the reader needs to understand.

## Practical Application
Step-by-step or example-driven content.

## Common Pitfalls
What to avoid and why.

## Checklist / Summary
Quick reference for future use.
```

{% elif content_type == "reference" %}
## Writing Reference Documentation

### Structure Pattern

```markdown
# API / Feature Reference

## Overview
One paragraph on what this covers.

## Quick Reference Table
| Item | Type | Description |
|------|------|-------------|
| ... | ... | ... |

## Detailed Reference

### Item 1
**Type:** `string`
**Default:** `"value"`
**Description:** What this does...

### Item 2
...
```

{% elif content_type == "tutorial" %}
## Writing Tutorials

### Structure Pattern

```markdown
# Tutorial: Build X

## What You'll Learn
- Outcome 1
- Outcome 2

## Prerequisites
- Requirement 1
- Requirement 2

## Step 1: Setup
Do this first...

## Step 2: Implementation
Then do this...

## Step 3: Testing
Verify it works...

## Next Steps
Where to go from here...
```

{% elif content_type == "checklist" %}
## Writing Checklists

### Structure Pattern

```markdown
# [Topic] Checklist

## Before Starting
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Main Tasks
- [ ] Task 1 - Brief description
- [ ] Task 2 - Brief description

## Verification
- [ ] Check 1
- [ ] Check 2

## Common Issues
- Issue → Solution
```

{% endif %}

---

## Design Best Practices

### 1. Focus on One Thing

```yaml
# BAD: Too broad
name: everything-about-python

# GOOD: Focused
name: python-testing-patterns
name: python-async-guide
name: python-packaging
```

### 2. Make Variables Meaningful

```yaml
# BAD: Generic names
variables:
  option1:
    enum: [a, b, c]

# GOOD: Descriptive names
variables:
  deployment_target:
    description: Where the application will run
    enum: [local, staging, production]
```

### 3. Provide Sensible Defaults

```yaml
# The most common choice should be the default
variables:
  language:
    enum: [python, javascript, go, rust]
    default: python  # Most users start here
```

### 4. Keep Conditional Blocks Focused

```markdown
{% if language == "python" %}
<!-- 50 lines of Python content -->
{% elif language == "javascript" %}
<!-- 50 lines of JavaScript content -->
{% endif %}

<!-- NOT -->

{% if language == "python" %}
<!-- 500 lines mixing everything -->
{% endif %}
```

### 5. Test Your Skill

Before publishing, render the skill with different variable combinations:

```bash
# Test default values
aiskills render my-skill

# Test specific combinations
aiskills render my-skill --var language=python --var scale=large
```

---

## Skill Creation Checklist

### Metadata
- [ ] Name is unique and kebab-case
- [ ] Description explains what AND when to use
- [ ] Version follows semver (1.0.0)
- [ ] Tags are relevant and searchable
- [ ] Category fits the skill's domain

### Variables
- [ ] Each variable has a clear description
- [ ] Enums cover all reasonable options
- [ ] Defaults represent the common case
- [ ] Variable names are self-documenting

### Content
- [ ] Opening explains the skill's value
- [ ] Examples are complete and runnable
- [ ] Conditionals render correctly for all variable combos
- [ ] No broken Jinja2 syntax
- [ ] Markdown renders properly

### Quality
- [ ] Content is accurate and up-to-date
- [ ] Code examples are tested
- [ ] Writing is clear and concise
- [ ] No spelling/grammar errors
