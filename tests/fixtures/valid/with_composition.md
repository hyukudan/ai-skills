---
name: composite-skill
description: A skill that extends and includes other skills
version: 1.0.0
tags:
  - composition
  - extends
  - includes
extends: base-skill@1.0.0
includes:
  - helper-skill@^2.0.0
  - utility-skill@>=1.5.0
---

# Composite Skill

This skill demonstrates composition through extends and includes.

## Composition

This skill extends `base-skill` to inherit its core functionality,
and includes additional capabilities from helper and utility skills.

### Extended From

- `base-skill@1.0.0`: Provides base functionality

### Included Skills

- `helper-skill`: Additional helper methods
- `utility-skill`: Common utility functions
