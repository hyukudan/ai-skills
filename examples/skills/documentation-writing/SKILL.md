---
name: documentation-writing
description: |
  Technical documentation writing guide for software projects. Use when writing
  READMEs, API documentation, architecture docs, or user guides. Covers documentation
  structure, writing style, and tools for different documentation types.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [documentation, writing, technical-writing, readme, api-docs]
category: development/documentation
variables:
  doc_type:
    type: string
    description: Type of documentation
    enum: [readme, api, architecture, user-guide, all]
    default: readme
  audience:
    type: string
    description: Target audience
    enum: [developers, end-users, internal-team, open-source]
    default: developers
---

# Documentation Writing Guide

## Philosophy

**Documentation is the user interface for your code.** Good docs make the difference between adoption and abandonment.

### Core Principles

1. **Write for your reader** - Not yourself, not your ego
2. **Show, don't tell** - Examples beat explanations
3. **Keep it current** - Outdated docs are worse than none
4. **Make it findable** - Structure matters as much as content

> "Documentation is a love letter that you write to your future self." — Damian Conway

---

{% if doc_type == "readme" or doc_type == "all" %}
## README Structure

### Essential Sections

```markdown
# Project Name

One-line description of what this does.

## Quick Start

​```bash
npm install project-name
​```

​```javascript
import { feature } from 'project-name';
feature.doThing();
​```

## Features

- **Feature 1** - Brief description
- **Feature 2** - Brief description
- **Feature 3** - Brief description

## Installation

Detailed installation instructions...

## Usage

### Basic Example

​```javascript
// Code example with comments
​```

### Advanced Usage

​```javascript
// More complex example
​```

## API Reference

Link to full API docs or brief reference...

## Contributing

Link to CONTRIBUTING.md or brief guidelines...

## License

MIT © Your Name
```

### README Best Practices

**Lead with value:**
```markdown
# BAD
MyLib is a JavaScript library written in TypeScript that provides...

# GOOD
Convert any date format in one line:
​```javascript
convert('2024-01-15').to('YYYY/MM/DD') // "2024/01/15"
​```
```

**Working examples first:**
```markdown
# BAD
## Installation
## Configuration
## API Reference
## Examples (page 47)

# GOOD
## Quick Start (working example in 30 seconds)
## Installation
## More Examples
## API Reference
```

**Badges that matter:**
```markdown
<!-- Useful badges -->
![Build Status](...)
![npm version](...)
![License](...)

<!-- Skip vanity badges -->
<!-- Downloads, stars, etc. don't help users -->
```

{% endif %}

---

{% if doc_type == "api" or doc_type == "all" %}
## API Documentation

### Endpoint Documentation Template

```markdown
## Create User

Creates a new user account.

### Request

​```
POST /api/v1/users
​```

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | Bearer token |
| Content-Type | Yes | application/json |

**Body:**
​```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
​```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Valid email address |
| name | string | Yes | Display name (2-100 chars) |
| role | string | No | One of: user, admin. Default: user |

### Response

**Success (201 Created):**
​```json
{
  "data": {
    "id": "usr_123abc",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
​```

**Error (422 Unprocessable Entity):**
​```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
​```

### Example

​```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "John Doe"}'
​```
```

### OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: |
    API for managing users and resources.

    ## Authentication
    All endpoints require Bearer token authentication.

paths:
  /users:
    post:
      summary: Create a new user
      description: |
        Creates a new user account with the specified details.
        Requires admin privileges.
      tags:
        - Users
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            example:
              email: user@example.com
              name: John Doe
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '422':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    CreateUserRequest:
      type: object
      required:
        - email
        - name
      properties:
        email:
          type: string
          format: email
          description: User's email address
        name:
          type: string
          minLength: 2
          maxLength: 100
          description: Display name
```

{% endif %}

---

{% if doc_type == "architecture" or doc_type == "all" %}
## Architecture Documentation

### Architecture Decision Records (ADR)

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
We need a database for storing user data, transactions, and analytics.
Requirements:
- ACID compliance for financial transactions
- Complex queries for analytics
- Horizontal read scaling
- Strong ecosystem and tooling

## Decision
We will use PostgreSQL as our primary database.

## Alternatives Considered

### MySQL
- Pro: Familiar to team
- Con: Less robust JSON support
- Con: Weaker window functions

### MongoDB
- Pro: Flexible schema
- Con: No ACID for multi-document transactions (at the time)
- Con: More complex for relational data

## Consequences

### Positive
- Strong ACID guarantees
- Excellent JSON/JSONB support
- Rich query capabilities
- Large community and tooling

### Negative
- Team needs PostgreSQL training
- More complex sharding than MongoDB
- Schema migrations require planning

## References
- [PostgreSQL vs MySQL comparison](...)
- [Team discussion notes](...)
```

### System Design Document

```markdown
# Order Processing System

## Overview
System for processing customer orders from receipt to fulfillment.

## Architecture

​```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web App   │────▶│   API GW    │────▶│  Order Svc  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
              ┌─────▼─────┐            ┌───────▼───────┐          ┌───────▼───────┐
              │ Inventory │            │   Payment     │          │  Notification │
              │  Service  │            │   Service     │          │    Service    │
              └───────────┘            └───────────────┘          └───────────────┘
​```

## Components

### Order Service
**Responsibility:** Orchestrates order lifecycle
**Technology:** Python/FastAPI
**Data Store:** PostgreSQL

### Inventory Service
**Responsibility:** Stock management, reservation
**Technology:** Go
**Data Store:** PostgreSQL + Redis cache

## Data Flow

1. User submits order via Web App
2. API Gateway validates authentication
3. Order Service creates order record (PENDING)
4. Inventory Service reserves stock
5. Payment Service processes payment
6. Order updated to CONFIRMED
7. Notification Service sends confirmation

## Failure Handling

| Scenario | Handling |
|----------|----------|
| Payment fails | Release inventory, notify user |
| Inventory unavailable | Reject order, notify user |
| Notification fails | Retry with backoff, don't block order |
```

{% endif %}

---

{% if doc_type == "user-guide" or doc_type == "all" %}
## User Guide Writing

### Structure for End Users

```markdown
# Getting Started with ProductName

## What You'll Learn
By the end of this guide, you'll be able to:
- Create your first project
- Invite team members
- Set up automated workflows

## Prerequisites
- A ProductName account ([sign up here](link))
- Basic familiarity with spreadsheets

## Step 1: Create Your First Project

1. Click the **+ New Project** button in the top right
2. Enter a project name (e.g., "My First Project")
3. Select a template or start blank
4. Click **Create**

![Screenshot of new project dialog](images/new-project.png)

> **Tip:** Use templates for common project types to save setup time.

## Step 2: Add Your Data

You can add data in three ways:

### Option A: Manual Entry
Click any cell and start typing...

### Option B: Import from CSV
1. Click **File > Import**
2. Select your CSV file
3. Map columns to fields

### Option C: Connect to External Source
[See Integration Guide](integrations.md)

## Common Issues

### "Permission Denied" Error
**Cause:** You don't have edit access to this project.
**Solution:** Ask the project owner to grant you Editor access.

### Data Not Syncing
**Cause:** Connection to external source may be interrupted.
**Solution:**
1. Check your internet connection
2. Re-authenticate the integration (Settings > Integrations)
3. Contact support if issue persists

## Next Steps
- [Advanced Features Guide](advanced.md)
- [API Documentation](api.md)
- [Video Tutorials](videos.md)
```

### Writing for Different Audiences

{% if audience == "developers" %}
**For Developers:**
- Lead with code examples
- Include error handling
- Explain the "why" not just "how"
- Link to source code
- Provide complete, runnable examples
{% elif audience == "end-users" %}
**For End Users:**
- Use simple language (no jargon)
- Include screenshots
- Provide step-by-step instructions
- Anticipate common mistakes
- Include troubleshooting section
{% elif audience == "internal-team" %}
**For Internal Team:**
- Include context and decisions
- Link to relevant discussions
- Document tribal knowledge
- Include runbooks for operations
- Keep update history
{% elif audience == "open-source" %}
**For Open Source:**
- Clear contribution guidelines
- Code of conduct
- Issue/PR templates
- Beginner-friendly labels
- Acknowledgment of contributors
{% endif %}

{% endif %}

---

## Writing Style Guide

### Be Concise

```markdown
# BAD
In order to be able to install the package, you will first need to make
sure that you have Node.js installed on your system.

# GOOD
Install Node.js first, then run:
​```bash
npm install package-name
​```
```

### Use Active Voice

```markdown
# BAD (passive)
The configuration file should be created by the user.

# GOOD (active)
Create a configuration file:
​```bash
touch config.json
​```
```

### Be Specific

```markdown
# BAD
The function takes some parameters and returns a result.

# GOOD
`calculateTax(amount: number, rate: number)` returns the tax amount.
​```javascript
calculateTax(100, 0.1) // Returns 10
​```
```

### Use Consistent Terminology

```markdown
# BAD
Create a new repo... clone the repository... pull the project...

# GOOD
Create a new repository... clone the repository... pull from the repository...
```

---

## Documentation Tools

### Static Site Generators

| Tool | Best For | Language |
|------|----------|----------|
| Docusaurus | React projects | JavaScript |
| MkDocs | Python projects | Python |
| GitBook | General docs | Any |
| Sphinx | Python API docs | Python |
| VitePress | Vue projects | JavaScript |

### API Documentation

| Tool | Type | Features |
|------|------|----------|
| Swagger/OpenAPI | Spec-first | Interactive UI |
| Redoc | OpenAPI renderer | Clean design |
| Stoplight | API platform | Design + docs |
| Postman | Collection-based | Testing + docs |

### Diagrams

```markdown
# Mermaid (embed in markdown)
​```mermaid
graph LR
    A[Client] --> B[API Gateway]
    B --> C[Service A]
    B --> D[Service B]
​```

# PlantUML
# draw.io / diagrams.net
# Excalidraw (hand-drawn style)
```

---

## Documentation Checklist

### Before Publishing
- [ ] All code examples tested and working
- [ ] Links verified (no 404s)
- [ ] Screenshots current
- [ ] Spelling and grammar checked
- [ ] Consistent formatting

### Content Quality
- [ ] Answers "what does this do?"
- [ ] Answers "how do I use it?"
- [ ] Includes working examples
- [ ] Covers common errors
- [ ] Has clear navigation

### Maintenance
- [ ] Versioned with code
- [ ] Review process defined
- [ ] Update triggers identified
- [ ] Feedback mechanism exists
