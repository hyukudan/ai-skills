---
name: configurable-skill
description: A skill with configurable variables
version: 2.1.0
tags:
  - configurable
  - variables
variables:
  username:
    type: string
    description: The user's display name
    default: "Guest"
  enable_logging:
    type: boolean
    description: Whether to enable debug logging
    default: false
  max_retries:
    type: integer
    description: Maximum number of retry attempts
    default: 3
    min: 1
    max: 10
  temperature:
    type: number
    description: Model temperature setting
    default: 0.7
    min: 0.0
    max: 2.0
---

# Configurable Skill

This skill demonstrates variable definitions with constraints.

## Variables

- `username`: String variable with default value
- `enable_logging`: Boolean toggle for debugging
- `max_retries`: Integer with min/max constraints
- `temperature`: Number with decimal constraints
