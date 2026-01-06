---
name: invalid-version-skill
description: A skill with invalid version constraint format
version: 1.0.0
tags:
  - invalid
  - version
dependencies:
  some-skill: ">>> not a valid version <<<"
  another-skill: "version:latest"
  bad-range: "1.0.0 to 2.0.0"
---

# Invalid Version Skill

This skill has malformed version constraints in its dependencies.
