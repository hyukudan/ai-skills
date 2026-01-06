---
name: dependent-skill
description: A skill with external dependencies
version: 1.5.0
tags:
  - dependencies
  - advanced
dependencies:
  core-utils: ">=1.0.0"
  data-processor: "^2.0.0"
  legacy-compat: "~1.2.3"
  exact-version: "3.0.0"
  range-version: ">=1.0.0,<2.0.0"
---

# Dependent Skill

This skill requires other skills to function properly.

## Dependencies

- `core-utils`: Any version 1.0.0 or higher
- `data-processor`: Compatible with 2.x.x
- `legacy-compat`: Patch-level compatible with 1.2.3
- `exact-version`: Exactly version 3.0.0
- `range-version`: Between 1.0.0 and 2.0.0 (exclusive)
