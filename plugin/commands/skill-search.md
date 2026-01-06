---
name: skill-search
description: Search for AI skills by query
arguments:
  - name: query
    description: Search query (semantic or text-based)
    required: true
---

# Search Skills: {{ query }}

Use the `skill_search` MCP tool with query "{{ query }}" to find relevant skills.

Present the results showing:
- Skill name and relevance score
- Brief description
- Tags

If the user seems interested in a specific skill, offer to read it using `skill_read`.

If no results are found:
1. Suggest alternative search terms
2. Try a text-based search with `text_only: true`
