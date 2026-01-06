"""REST API for aiskills - universal HTTP interface.

Provides:
- RESTful endpoints for skill operations
- OpenAI-compatible function calling format
- CORS support for browser clients
"""

from .server import create_app, run_server, main
from .models import (
    SearchRequest,
    SearchResponse,
    ReadRequest,
    ReadResponse,
    ListResponse,
    SuggestRequest,
    SuggestResponse,
    SkillInfo,
    SearchResult,
    OpenAIToolsResponse,
    OpenAIFunctionCall,
    OpenAIFunctionResponse,
)

__all__ = [
    "create_app",
    "run_server",
    "main",
    "SearchRequest",
    "SearchResponse",
    "ReadRequest",
    "ReadResponse",
    "ListResponse",
    "SuggestRequest",
    "SuggestResponse",
    "SkillInfo",
    "SearchResult",
    "OpenAIToolsResponse",
    "OpenAIFunctionCall",
    "OpenAIFunctionResponse",
]
