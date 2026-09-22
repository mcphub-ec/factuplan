"""
Factuplan MCP Server — HTTP entry point.

Reads MCP_PORT and MCP_TRANSPORT_MODE from the environment and starts
uvicorn with the appropriate FastMCP transport app.
"""

import os

import uvicorn

import server  # noqa: F401 — registers all tools as a side-effect

app = server.mcp.streamable_http_app()

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8000))
    transport_mode = os.getenv("MCP_TRANSPORT_MODE", "sse").lower()
    print(f"Starting Factuplan MCP Server on http://0.0.0.0:{port}/mcp ({transport_mode})")
    if transport_mode == "sse":
        run_app = server.mcp.sse_app()
    elif transport_mode == "http_stream":
        run_app = server.mcp.streamable_http_app()
    else:
        raise ValueError(f"Unknown transport mode: {transport_mode}")
    uvicorn.run(run_app, host=os.getenv("MCP_HOST", "0.0.0.0"), port=port)  # nosec: B104
