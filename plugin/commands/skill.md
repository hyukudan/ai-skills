---
name: skill
description: Read an AI skill by name and display its content
arguments:
  - name: name
    description: Name of the skill to read
    required: true
---

# Read Skill: {{ name }}

Use the `skill_read` MCP tool to read the skill named "{{ name }}".

If the skill is not found, use `skill_search` to find similar skills and suggest alternatives.

After reading the skill, apply its guidance to the current task if relevant.
