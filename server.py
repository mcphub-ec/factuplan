"""
Factuplan MCP Server
====================
MCP server for the Factuplan REST API v1 — certified electronic invoicing
platform for Ecuador (SRI).

Technical reference: docs/openapi.yaml

This module is the canonical runtime namespace. It re-exports config flags
and HTTP helpers, then imports tools.specs so every @mcp.tool() decorator
registers on the shared `mcp` instance.
"""

from config import (  # noqa: F401
    FACTUPLAN_BASE_URL,
    HTTP_TIMEOUT,
    logger,
)
from app import mcp  # noqa: F401
from _http import (  # noqa: F401
    _build_headers,
    _request,
    _json,
    _drop_none,
)

# Importing specs builds + registers all 23 tools via the data-driven factory.
import tools.specs  # noqa: F401, E402

__all__ = ["mcp", "_request", "_json", "_drop_none"]
