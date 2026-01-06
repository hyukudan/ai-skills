"""REST API Server for aiskills - universal HTTP interface."""

from __future__ import annotations

import json
from typing import Any

from .models import (
    ErrorResponse,
    ListResponse,
    OpenAIFunction,
    OpenAIFunctionCall,
    OpenAIFunctionParameters,
    OpenAIFunctionParameter,
    OpenAIFunctionResponse,
    OpenAITool,
    OpenAIToolsResponse,
    ReadRequest,
    ReadResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SkillInfo,
    SuggestRequest,
    SuggestResponse,
)


def create_app():
    """Create the FastAPI application."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        raise ImportError(
            "FastAPI not installed. Install with: pip install aiskills[api]"
        )

    app = FastAPI(
        title="aiskills API",
        description="Universal LLM-agnostic skills system API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Enable CORS for browser-based clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─────────────────────────────────────────────────────────────────
    # Health & Info
    # ─────────────────────────────────────────────────────────────────

    @app.get("/")
    async def root():
        """API root - basic info."""
        return {
            "name": "aiskills",
            "version": "0.1.0",
            "description": "Universal LLM-agnostic skills system",
            "docs": "/docs",
            "openai_tools": "/openai/tools",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    # ─────────────────────────────────────────────────────────────────
    # Skills API
    # ─────────────────────────────────────────────────────────────────

    @app.get("/skills", response_model=ListResponse)
    async def list_skills(
        global_only: bool = False,
        project_only: bool = False,
        category: str | None = None,
    ):
        """List all installed skills."""
        from ..core.manager import get_manager

        manager = get_manager()
        skills = manager.list_installed(
            global_only=global_only,
            project_only=project_only,
        )

        # Filter by category
        if category:
            skills = [s for s in skills if s.manifest.category == category]

        skill_infos = [
            SkillInfo(
                name=s.manifest.name,
                version=s.manifest.version,
                description=s.manifest.description,
                tags=s.manifest.tags,
                category=s.manifest.category,
                source=s.source,
            )
            for s in skills
        ]

        project_count = sum(1 for s in skills if s.source == "project")
        global_count = len(skills) - project_count

        return ListResponse(
            skills=skill_infos,
            total=len(skills),
            project_count=project_count,
            global_count=global_count,
        )

    @app.get("/skills/{name}", response_model=ReadResponse)
    async def get_skill(name: str, raw: bool = False):
        """Get a skill by name."""
        from ..core.manager import get_manager

        manager = get_manager()
        skill = manager.get(name)

        if skill is None:
            raise HTTPException(status_code=404, detail=f"Skill not found: {name}")

        content = manager.read(name, raw=raw) if not raw else skill.content

        return ReadResponse(
            name=name,
            content=content,
            metadata=SkillInfo(
                name=skill.manifest.name,
                version=skill.manifest.version,
                description=skill.manifest.description,
                tags=skill.manifest.tags,
                category=skill.manifest.category,
                source=skill.source,
            ),
        )

    @app.post("/skills/read", response_model=ReadResponse)
    async def read_skill(request: ReadRequest):
        """Read a skill with optional variables."""
        from ..core.manager import get_manager

        manager = get_manager()
        skill = manager.get(request.name)

        if skill is None:
            raise HTTPException(
                status_code=404, detail=f"Skill not found: {request.name}"
            )

        if request.raw:
            content = skill.content
        else:
            content = manager.read(
                request.name,
                variables=request.variables,
            )

        return ReadResponse(
            name=request.name,
            content=content,
            metadata=SkillInfo(
                name=skill.manifest.name,
                version=skill.manifest.version,
                description=skill.manifest.description,
                tags=skill.manifest.tags,
                category=skill.manifest.category,
                source=skill.source,
            ),
        )

    @app.post("/skills/search", response_model=SearchResponse)
    async def search_skills(request: SearchRequest):
        """Search for skills."""
        from ..core.registry import get_registry

        registry = get_registry()

        if request.text_only:
            results = registry.search_text(request.query, limit=request.limit)
            return SearchResponse(
                query=request.query,
                type="text",
                results=[
                    SearchResult(
                        skill=SkillInfo(
                            name=idx.name,
                            version=idx.version,
                            description=idx.description,
                            tags=idx.tags,
                            category=idx.category,
                            source=idx.source,
                        ),
                        score=None,
                    )
                    for idx in results
                ],
                total=len(results),
            )
        else:
            try:
                results = registry.search(
                    query=request.query,
                    limit=request.limit,
                    tags=request.tags,
                    category=request.category,
                    min_score=request.min_score,
                )
                return SearchResponse(
                    query=request.query,
                    type="semantic",
                    results=[
                        SearchResult(
                            skill=SkillInfo(
                                name=idx.name,
                                version=idx.version,
                                description=idx.description,
                                tags=idx.tags,
                                category=idx.category,
                                source=idx.source,
                            ),
                            score=round(score, 3),
                        )
                        for idx, score in results
                    ],
                    total=len(results),
                )
            except Exception as e:
                if "not installed" in str(e).lower():
                    # Fallback to text search
                    results = registry.search_text(request.query, limit=request.limit)
                    return SearchResponse(
                        query=request.query,
                        type="text",
                        results=[
                            SearchResult(
                                skill=SkillInfo(
                                    name=idx.name,
                                    version=idx.version,
                                    description=idx.description,
                                    tags=idx.tags,
                                    category=idx.category,
                                    source=idx.source,
                                ),
                                score=None,
                            )
                            for idx in results
                        ],
                        total=len(results),
                    )
                raise

    @app.post("/skills/suggest", response_model=SuggestResponse)
    async def suggest_skills(request: SuggestRequest):
        """Suggest relevant skills based on context."""
        from ..core.registry import get_registry

        registry = get_registry()

        try:
            results = registry.search(
                query=request.context,
                limit=request.limit,
                min_score=0.3,
            )

            return SuggestResponse(
                context=request.context,
                suggestions=[
                    SearchResult(
                        skill=SkillInfo(
                            name=idx.name,
                            version=idx.version,
                            description=idx.description,
                            tags=idx.tags,
                            category=idx.category,
                            source=idx.source,
                        ),
                        score=round(score, 3),
                    )
                    for idx, score in results
                ],
            )
        except Exception:
            return SuggestResponse(context=request.context, suggestions=[])

    # ─────────────────────────────────────────────────────────────────
    # OpenAI Compatible Endpoints
    # ─────────────────────────────────────────────────────────────────

    @app.get("/openai/tools", response_model=OpenAIToolsResponse)
    async def get_openai_tools():
        """Get tool definitions in OpenAI function calling format.

        Use these definitions to configure Custom GPTs or
        OpenAI function calling.
        """
        tools = [
            OpenAITool(
                function=OpenAIFunction(
                    name="skill_search",
                    description="Search for AI skills by semantic similarity or text matching. Returns relevant skills for a given query.",
                    parameters=OpenAIFunctionParameters(
                        properties={
                            "query": OpenAIFunctionParameter(
                                type="string",
                                description="Search query to find relevant skills",
                            ),
                            "limit": OpenAIFunctionParameter(
                                type="integer",
                                description="Maximum number of results (1-50)",
                                default=10,
                            ),
                            "text_only": OpenAIFunctionParameter(
                                type="boolean",
                                description="Use text search instead of semantic",
                                default=False,
                            ),
                        },
                        required=["query"],
                    ),
                ),
            ),
            OpenAITool(
                function=OpenAIFunction(
                    name="skill_read",
                    description="Read the full content of a skill by name. Returns the skill's instructions and guidelines.",
                    parameters=OpenAIFunctionParameters(
                        properties={
                            "name": OpenAIFunctionParameter(
                                type="string",
                                description="Name of the skill to read",
                            ),
                            "variables": OpenAIFunctionParameter(
                                type="object",
                                description="Optional variables to render in the skill template",
                            ),
                        },
                        required=["name"],
                    ),
                ),
            ),
            OpenAITool(
                function=OpenAIFunction(
                    name="skill_list",
                    description="List all available skills. Returns skill names, versions, and descriptions.",
                    parameters=OpenAIFunctionParameters(
                        properties={
                            "category": OpenAIFunctionParameter(
                                type="string",
                                description="Filter by category",
                            ),
                        },
                        required=[],
                    ),
                ),
            ),
            OpenAITool(
                function=OpenAIFunction(
                    name="skill_suggest",
                    description="Suggest relevant skills based on current context or task description.",
                    parameters=OpenAIFunctionParameters(
                        properties={
                            "context": OpenAIFunctionParameter(
                                type="string",
                                description="Current context or task description",
                            ),
                            "limit": OpenAIFunctionParameter(
                                type="integer",
                                description="Maximum suggestions (1-10)",
                                default=3,
                            ),
                        },
                        required=["context"],
                    ),
                ),
            ),
        ]

        return OpenAIToolsResponse(tools=tools)

    @app.post("/openai/call", response_model=OpenAIFunctionResponse)
    async def call_openai_function(request: OpenAIFunctionCall):
        """Execute a function call in OpenAI format.

        This endpoint accepts function calls in the format returned
        by OpenAI's function calling and returns results.
        """
        name = request.name
        args = request.arguments

        try:
            if name == "skill_search":
                search_req = SearchRequest(**args)
                result = await search_skills(search_req)
                content = result.model_dump_json()

            elif name == "skill_read":
                read_req = ReadRequest(**args)
                result = await read_skill(read_req)
                content = result.model_dump_json()

            elif name == "skill_list":
                category = args.get("category")
                result = await list_skills(category=category)
                content = result.model_dump_json()

            elif name == "skill_suggest":
                suggest_req = SuggestRequest(**args)
                result = await suggest_skills(suggest_req)
                content = result.model_dump_json()

            else:
                content = json.dumps({"error": f"Unknown function: {name}"})

        except Exception as e:
            content = json.dumps({"error": str(e)})

        return OpenAIFunctionResponse(name=name, content=content)

    return app


def run_server(host: str = "0.0.0.0", port: int = 8420, reload: bool = False):
    """Run the API server."""
    try:
        import uvicorn
    except ImportError:
        raise ImportError(
            "uvicorn not installed. Install with: pip install aiskills[api]"
        )

    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)


def main():
    """Entry point for API server."""
    run_server()


if __name__ == "__main__":
    main()
