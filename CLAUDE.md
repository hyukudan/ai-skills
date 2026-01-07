# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Skills** is a universal, LLM-agnostic skills management system that transforms markdown files into semantically searchable tools for any AI agent (Claude, ChatGPT, Gemini, Ollama). Skills are markdown files with YAML frontmatter that get indexed for semantic + text hybrid search.

## Common Commands

```bash
# Development setup
pip install -e ".[all,dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=aiskills --cov-report=html

# Run a single test file
pytest tests/core/test_router.py -v

# Run a specific test
pytest tests/core/test_router.py::test_use_returns_best_match -v

# Multi-LLM acceptance tests
pytest tests/integration/test_multi_llm.py -v

# Type checking (strict mode)
mypy src/aiskills

# Linting
ruff check src/aiskills

# Format code
ruff format src/aiskills

# CLI usage (after install)
aiskills use "debug python memory leak"
aiskills search "how to test async code"
aiskills browse --context "database migrations"
aiskills list

# Start servers
aiskills api serve           # REST API on localhost:8000
aiskills mcp serve            # MCP server for Claude Desktop
```

## Architecture

```
┌─────────────────────────────────────────┐
│         INTERFACES                      │
│  CLI (Typer) │ REST API │ MCP │ Plugin  │
└────────────────┬────────────────────────┘
                 │
          ┌──────▼──────┐
          │ SkillRouter │ (Central Intelligence)
          └──────┬──────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼────┐   ┌──▼──────┐
│Manager│   │Registry│   │ Scoping │
└───────┘   └────────┘   └─────────┘
```

**Key modules in `src/aiskills/`:**

- `core/router.py` - Central intelligence for skill discovery. All interfaces use this.
- `core/manager.py` - Orchestrates skill operations (load, install, cache)
- `core/registry.py` - Indexes skills using vector embeddings + BM25 hybrid search
- `core/loader.py` - Parses SKILL.md files and handles local overrides (.local.md)
- `core/scoping.py` - Declarative matching beyond semantic search (paths, languages, triggers)
- `search/hybrid.py` - Combines semantic embeddings with BM25 text search
- `api/server.py` - FastAPI REST server with OpenAI-compatible endpoints
- `mcp/server.py` - Model Context Protocol server for Claude Desktop

## Core Patterns

### Progressive Disclosure (3 Phases)
The system optimizes context window usage across three phases:
1. **Browse** - Lightweight metadata only (name, description, tokens_est)
2. **Load** - Full rendered skill content
3. **Resource** - Additional resources loaded on-demand

```python
# Phase 1
router.browse(context="python debugging")  # Returns SkillBrowseInfo

# Phase 2
result = router.use("debug memory leak")   # Returns UseResult with full content

# Phase 3
resource = router.resource(skill_name, "templates")  # Load extra resources
```

### Declarative Scoping
Skills define constraints that go beyond semantic matching:
```yaml
scope:
  paths: ["src/api/**", "migrations/**"]
  languages: [python, sql]
  triggers: [migrate, alembic]
priority: 75
```

### Local Overrides
Team skills can be customized per-project via `.local.md` files (gitignored):
```
my-skill/
├── SKILL.md          # Shared, versioned
└── SKILL.local.md    # Private overrides, deep-merged
```

### Skill Composition
Skills can include other skills without duplication:
```markdown
@include skill:python-debugging
@include snippets/patterns.md
```

## Key Architectural Decisions

1. **Lazy Loading** - Manager, Router, Registry use lazy loading to avoid circular imports
2. **Hybrid Search** - BM25 text + semantic embeddings for robustness when one fails
3. **Provider-Agnostic** - Single router serves CLI, REST API, MCP, and plugin equally
4. **Async-Ready** - FastAPI, MCP, and tests all use asyncio

## Commit Style

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`
