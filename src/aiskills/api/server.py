"""REST API Server for aiskills - universal HTTP interface."""

from __future__ import annotations

import json
from typing import Any

from .models import (
    BrowseRequest,
    BrowseResponse,
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
    ResourceListResponse,
    ResourceRequest,
    ResourceResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    ShouldInvokeRequest,
    ShouldInvokeResponse,
    SkillBrowseInfo,
    SkillInfo,
    SkillResourceInfo,
    SuggestRequest,
    SuggestResponse,
    UseRequest,
    UseResponse,
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

        content = skill.content if raw else manager.read(name)

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

    @app.post("/skills/use", response_model=UseResponse)
    async def use_skill(request: UseRequest):
        """Phase 2 (Load): Find and use the best matching skill.

        This is the primary endpoint for skill invocation. Describe what you
        need in natural language, and the system will find and return the
        most relevant skill with its content.

        Supports scoping context (active_paths, languages) for better matching.
        """
        from ..core.router import get_router

        router = get_router()
        result = router.use(
            context=request.context,
            variables=request.variables,
            active_paths=request.active_paths,
            languages=request.languages,
        )

        return UseResponse(
            skill_name=result.skill_name,
            content=result.content,
            score=result.score,
            matched_query=result.matched_query,
            available_resources=result.available_resources,
            tokens_used=result.tokens_used,
        )

    # ─────────────────────────────────────────────────────────────────
    # Auto-Discovery API
    # ─────────────────────────────────────────────────────────────────

    @app.post("/skills/should-invoke", response_model=ShouldInvokeResponse)
    async def should_invoke_skill(request: ShouldInvokeRequest):
        """Determine if a skill should be invoked based on user message.

        This endpoint analyzes the user's message and context to suggest
        whether a skill should be used. It checks:
        - Semantic similarity with available skills
        - Trigger keywords defined in skill scopes
        - File path and language context matching

        Use this to implement auto-invocation in your LLM integration.

        Example:
            POST /skills/should-invoke
            {
                "user_message": "I have a memory leak in my Python app",
                "languages": ["python"]
            }

            Response:
            {
                "should_invoke": true,
                "suggested_skill": "python-debugging",
                "confidence": 0.87,
                "reason": "Message matches debugging triggers and Python scope",
                "matched_triggers": ["memory leak"]
            }
        """
        from ..core.router import get_router
        from ..core.scoping import ScopeContext

        router = get_router()

        # Create scope context
        scope_ctx = ScopeContext(
            active_paths=request.active_paths or [],
            languages=request.languages or [],
            query=request.user_message,
        )

        # Get all skills and check triggers
        all_skills = router.registry.list_all()
        message_lower = request.user_message.lower()

        # Check for trigger matches
        trigger_matches: dict[str, list[str]] = {}
        for skill_idx in all_skills:
            skill = router.manager.get(skill_idx.name)
            if skill and skill.manifest.scope:
                triggers = skill.manifest.scope.triggers or []
                matched = [t for t in triggers if t.lower() in message_lower]
                if matched:
                    trigger_matches[skill_idx.name] = matched

        # Do semantic search
        try:
            semantic_results = router.registry.search(
                query=request.user_message,
                limit=5,
                min_score=0.3,
            )
            semantic_matches = {idx.name: score for idx, score in semantic_results}
        except Exception:
            semantic_matches = {}

        # Combine trigger and semantic matches
        combined_scores: dict[str, float] = {}

        for name, triggers in trigger_matches.items():
            # Trigger match gives a base score
            combined_scores[name] = 0.5 + (0.1 * len(triggers))

        for name, score in semantic_matches.items():
            if name in combined_scores:
                # Combine with trigger score
                combined_scores[name] = min(1.0, combined_scores[name] + score * 0.5)
            else:
                combined_scores[name] = score * 0.8  # Pure semantic match

        # Apply scope filtering
        if request.active_paths or request.languages:
            filtered = router.scope_matcher.filter_by_scope(all_skills, scope_ctx)
            scope_matched_names = {idx.name for idx, _ in filtered}

            # Boost scores for scope-matched skills
            for name in combined_scores:
                if name in scope_matched_names:
                    combined_scores[name] = min(1.0, combined_scores[name] + 0.1)

        if not combined_scores:
            return ShouldInvokeResponse(
                should_invoke=False,
                confidence=0.0,
                reason="No matching skills found for this message",
            )

        # Get best match
        sorted_matches = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        best_name, best_score = sorted_matches[0]
        matched_triggers = trigger_matches.get(best_name, [])

        # Determine if we should invoke (threshold: 0.4)
        should_invoke = best_score >= 0.4

        # Build reason
        reasons = []
        if matched_triggers:
            reasons.append(f"Matched triggers: {', '.join(matched_triggers)}")
        if best_name in semantic_matches:
            reasons.append(f"Semantic match score: {semantic_matches[best_name]:.2f}")
        reason = ". ".join(reasons) if reasons else "Score threshold met"

        # Get alternatives
        alternatives = [name for name, _ in sorted_matches[1:4]]

        return ShouldInvokeResponse(
            should_invoke=should_invoke,
            suggested_skill=best_name if should_invoke else None,
            confidence=round(best_score, 3),
            reason=reason,
            matched_triggers=matched_triggers,
            alternatives=alternatives,
        )

    # ─────────────────────────────────────────────────────────────────
    # Progressive Disclosure API (Browse → Load → Use)
    # ─────────────────────────────────────────────────────────────────

    @app.post("/skills/browse", response_model=BrowseResponse)
    async def browse_skills(request: BrowseRequest):
        """Phase 1 (Browse): Get lightweight skill metadata only.

        Returns SkillBrowseInfo without loading full content.
        Use this to discover relevant skills and decide which to load.

        Supports:
        - Semantic search (via context query)
        - Scope filtering (via active_paths, languages)
        - Priority-based sorting
        """
        from ..core.router import get_router

        router = get_router()
        results = router.browse(
            context=request.context,
            active_paths=request.active_paths,
            languages=request.languages,
            limit=request.limit,
            min_score=request.min_score,
        )

        # Convert to API model
        browse_infos = [
            SkillBrowseInfo(
                name=r.name,
                description=r.description,
                version=r.version,
                tags=r.tags,
                category=r.category,
                tokens_est=r.tokens_est,
                priority=r.priority,
                precedence=r.precedence,
                scope_paths=r.scope_paths,
                scope_languages=r.scope_languages,
                scope_triggers=r.scope_triggers,
                source=r.source,
                has_variables=r.has_variables,
                has_dependencies=r.has_dependencies,
            )
            for r in results
        ]

        return BrowseResponse(
            skills=browse_infos,
            total=len(browse_infos),
            query=request.context,
        )

    @app.get("/skills/{name}/resources", response_model=ResourceListResponse)
    async def list_skill_resources(name: str):
        """Phase 3 (Use) preparation: List available resources for a skill.

        Returns information about templates, references, scripts, and assets
        that can be loaded on-demand.
        """
        from ..core.router import get_router

        router = get_router()
        resources = router.list_resources(name)

        resource_infos = [
            SkillResourceInfo(
                resource_type=r.resource_type,
                path=r.path,
                name=r.name,
                size_bytes=r.size_bytes,
                tokens_est=r.tokens_est,
                requires_execution=r.requires_execution,
                allowed=r.allowed,
            )
            for r in resources
        ]

        return ResourceListResponse(
            skill_name=name,
            resources=resource_infos,
            total=len(resource_infos),
        )

    @app.post("/skills/resource", response_model=ResourceResponse)
    async def get_skill_resource(request: ResourceRequest):
        """Phase 3 (Use): Load a specific resource from a skill.

        Loads additional resources (templates, references, scripts, assets)
        on-demand after using the main skill content.
        """
        from ..core.router import get_router

        router = get_router()

        # Get resource content
        content = router.resource(request.skill_name, request.resource_name)

        if content is None:
            raise HTTPException(
                status_code=404,
                detail=f"Resource '{request.resource_name}' not found in skill '{request.skill_name}'",
            )

        # Determine resource type
        resources = router.list_resources(request.skill_name)
        resource_type = "unknown"
        tokens_est = None
        for r in resources:
            if r.name == request.resource_name:
                resource_type = r.resource_type
                tokens_est = r.tokens_est
                break

        return ResourceResponse(
            skill_name=request.skill_name,
            resource_name=request.resource_name,
            content=content,
            resource_type=resource_type,
            tokens_est=tokens_est,
        )

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
                    name="use_skill",
                    description="Find and use the best AI skill for your current task. Describe what you need in natural language.",
                    parameters=OpenAIFunctionParameters(
                        properties={
                            "context": OpenAIFunctionParameter(
                                type="string",
                                description="Natural language description of what you need (e.g., 'debug python memory leak')",
                            ),
                            "variables": OpenAIFunctionParameter(
                                type="object",
                                description="Optional variables to customize the skill",
                            ),
                        },
                        required=["context"],
                    ),
                ),
            ),
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
            if name == "use_skill":
                use_req = UseRequest(**args)
                result = await use_skill(use_req)
                content = result.model_dump_json()

            elif name == "skill_search":
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
