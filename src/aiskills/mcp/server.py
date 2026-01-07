"""MCP Server for aiskills - exposes skills as MCP tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import (
    TOOL_DEFINITIONS,
    SkillCategoriesInput,
    SkillListInput,
    SkillReadInput,
    SkillSearchInput,
    SkillSuggestInput,
    SkillVarsInput,
    UseSkillInput,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aiskills.mcp")


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("aiskills")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["inputSchema"],
            )
            for tool in TOOL_DEFINITIONS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        try:
            if name == "use_skill":
                result = await handle_use_skill(arguments)
            elif name == "skill_search":
                result = await handle_skill_search(arguments)
            elif name == "skill_read":
                result = await handle_skill_read(arguments)
            elif name == "skill_list":
                result = await handle_skill_list(arguments)
            elif name == "skill_suggest":
                result = await handle_skill_suggest(arguments)
            elif name == "skill_categories":
                result = await handle_skill_categories(arguments)
            elif name == "skill_vars":
                result = await handle_skill_vars(arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.exception(f"Error in tool {name}")
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}),
                )
            ]

    return server


async def handle_skill_search(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_search tool call."""
    from ..core.registry import get_registry

    input_data = SkillSearchInput(**arguments)
    registry = get_registry()

    if input_data.text_only:
        # Text search
        results = registry.search_text(input_data.query, limit=input_data.limit)
        return {
            "type": "text_search",
            "query": input_data.query,
            "results": [
                {
                    "name": idx.name,
                    "version": idx.version,
                    "description": idx.description,
                    "tags": idx.tags,
                    "category": idx.category,
                }
                for idx in results
            ],
        }
    elif input_data.hybrid:
        # Hybrid search (semantic + BM25)
        try:
            results = registry.search_hybrid(
                query=input_data.query,
                limit=input_data.limit,
                tags=input_data.tags,
                category=input_data.category,
            )
            return {
                "type": "hybrid_search",
                "query": input_data.query,
                "results": [
                    {
                        "name": idx.name,
                        "version": idx.version,
                        "description": idx.description,
                        "tags": idx.tags,
                        "category": idx.category,
                        "score": round(score, 3),
                    }
                    for idx, score in results
                ],
            }
        except Exception as e:
            # Fallback to text search if hybrid fails
            error_msg = str(e)
            if "not installed" in error_msg.lower():
                results = registry.search_text(input_data.query, limit=input_data.limit)
                return {
                    "type": "text_search",
                    "query": input_data.query,
                    "note": "Hybrid search unavailable, using text search",
                    "results": [
                        {
                            "name": idx.name,
                            "version": idx.version,
                            "description": idx.description,
                            "tags": idx.tags,
                            "category": idx.category,
                        }
                        for idx in results
                    ],
                }
            raise
    else:
        # Semantic search
        try:
            results = registry.search(
                query=input_data.query,
                limit=input_data.limit,
                tags=input_data.tags,
                category=input_data.category,
            )
            return {
                "type": "semantic_search",
                "query": input_data.query,
                "results": [
                    {
                        "name": idx.name,
                        "version": idx.version,
                        "description": idx.description,
                        "tags": idx.tags,
                        "category": idx.category,
                        "score": round(score, 3),
                    }
                    for idx, score in results
                ],
            }
        except Exception as e:
            # Fallback to text search if semantic fails
            error_msg = str(e)
            if "not installed" in error_msg.lower():
                results = registry.search_text(input_data.query, limit=input_data.limit)
                return {
                    "type": "text_search",
                    "query": input_data.query,
                    "note": "Semantic search unavailable, using text search",
                    "results": [
                        {
                            "name": idx.name,
                            "version": idx.version,
                            "description": idx.description,
                            "tags": idx.tags,
                            "category": idx.category,
                        }
                        for idx in results
                    ],
                }
            raise


async def handle_skill_read(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_read tool call."""
    from ..core.manager import get_manager

    input_data = SkillReadInput(**arguments)
    manager = get_manager()

    try:
        content = manager.read(
            name=input_data.name,
            variables=input_data.variables,
            raw=input_data.raw,
        )

        # Also get metadata
        skill = manager.get(input_data.name)
        metadata = {}
        if skill:
            metadata = {
                "name": skill.manifest.name,
                "version": skill.manifest.version,
                "description": skill.manifest.description,
                "tags": skill.manifest.tags,
                "category": skill.manifest.category,
            }

        return {
            "name": input_data.name,
            "content": content,
            "metadata": metadata,
        }

    except FileNotFoundError:
        return {
            "error": f"Skill not found: {input_data.name}",
            "suggestion": "Use skill_search to find available skills",
        }


async def handle_skill_list(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_list tool call."""
    from ..core.manager import get_manager

    input_data = SkillListInput(**arguments)
    manager = get_manager()

    skills = manager.list_installed()

    # Filter by source if global_only
    if input_data.global_only:
        skills = [s for s in skills if s.source == "global"]

    # Filter by category
    if input_data.category:
        skills = [
            s for s in skills if s.manifest.category == input_data.category
        ]

    return {
        "total": len(skills),
        "skills": [
            {
                "name": s.manifest.name,
                "version": s.manifest.version,
                "description": s.manifest.description,
                "tags": s.manifest.tags,
                "category": s.manifest.category,
                "source": s.source,
            }
            for s in skills
        ],
    }


async def handle_skill_suggest(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_suggest tool call."""
    from ..core.registry import get_registry

    input_data = SkillSuggestInput(**arguments)
    registry = get_registry()

    # Use semantic search with the context
    try:
        results = registry.search(
            query=input_data.context,
            limit=input_data.limit,
            min_score=0.3,  # Only suggest if reasonably relevant
        )

        if not results:
            return {
                "context": input_data.context,
                "suggestions": [],
                "message": "No relevant skills found for this context",
            }

        return {
            "context": input_data.context,
            "suggestions": [
                {
                    "name": idx.name,
                    "description": idx.description,
                    "relevance": f"{round(score * 100)}%",
                    "reason": f"Matches context based on semantic similarity",
                }
                for idx, score in results
            ],
        }

    except Exception as e:
        error_msg = str(e)
        if "not installed" in error_msg.lower():
            return {
                "error": "Semantic search not available",
                "suggestion": "Install search extras: pip install aiskills[search]",
            }
        raise


async def handle_use_skill(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle use_skill tool call - the primary skill invocation interface."""
    from ..core.router import get_router

    input_data = UseSkillInput(**arguments)
    router = get_router()

    result = router.use(
        context=input_data.context,
        variables=input_data.variables,
    )

    return {
        "skill_name": result.skill_name,
        "content": result.content,
        "score": result.score,
        "matched_query": result.matched_query,
    }


async def handle_skill_categories(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_categories tool call."""
    from ..core.manager import get_manager
    from collections import defaultdict

    input_data = SkillCategoriesInput(**arguments)
    manager = get_manager()

    skills = manager.list_installed()

    # Group skills by category
    categories: dict[str, list[dict]] = defaultdict(list)
    uncategorized: list[dict] = []

    for skill in skills:
        skill_info = {
            "name": skill.manifest.name,
            "description": skill.manifest.description[:100] + "..."
            if len(skill.manifest.description) > 100
            else skill.manifest.description,
        }

        if skill.manifest.category:
            categories[skill.manifest.category].append(skill_info)
        else:
            uncategorized.append(skill_info)

    # Build response
    result = {
        "total_categories": len(categories),
        "total_skills": len(skills),
        "categories": {},
    }

    # Sort categories and build output
    for category in sorted(categories.keys()):
        if input_data.include_skills:
            result["categories"][category] = {
                "count": len(categories[category]),
                "skills": categories[category],
            }
        else:
            result["categories"][category] = {
                "count": len(categories[category]),
            }

    if uncategorized:
        if input_data.include_skills:
            result["uncategorized"] = {
                "count": len(uncategorized),
                "skills": uncategorized,
            }
        else:
            result["uncategorized"] = {"count": len(uncategorized)}

    return result


async def handle_skill_vars(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle skill_vars tool call."""
    from ..core.manager import get_manager

    input_data = SkillVarsInput(**arguments)
    manager = get_manager()

    try:
        skill = manager.get(input_data.name)
    except Exception:
        return {
            "error": f"Skill not found: {input_data.name}",
            "suggestion": "Use skill_list or skill_search to find available skills",
        }

    if skill is None:
        return {
            "error": f"Skill not found: {input_data.name}",
            "suggestion": "Use skill_list or skill_search to find available skills",
        }

    variables = skill.manifest.variables

    if not variables:
        return {
            "name": input_data.name,
            "variables": {},
            "message": "This skill has no configurable variables",
        }

    # Build detailed variable info
    var_info = {}
    for var_name, var_meta in variables.items():
        var_info[var_name] = {
            "type": var_meta.type,
            "description": var_meta.description,
            "default": var_meta.default,
            "required": var_meta.required,
        }
        if var_meta.enum:
            var_info[var_name]["allowed_values"] = var_meta.enum
        if var_meta.min is not None:
            var_info[var_name]["min"] = var_meta.min
        if var_meta.max is not None:
            var_info[var_name]["max"] = var_meta.max

    return {
        "name": input_data.name,
        "variables": var_info,
        "usage_hint": f"Use skill_read with variables parameter, e.g., skill_read(name='{input_data.name}', variables={{'var_name': 'value'}})",
    }


async def run_server() -> None:
    """Run the MCP server."""
    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for MCP server."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
