"""Data-driven tool registry + factory for the Factuplan MCP server.

Adapted from luismanuu/mcp-contifico tools/_registry.py.
Replaces hand-written @mcp.tool() shims with a declarative spec table
(tools.specs.SPECS) plus this factory.

Supported modes:
  - "params":           GET with optional query-param dict (query keys).
  - "body":             POST/PUT with required body keys + drop-none optionals.
  - "body_literal":     POST/PUT with a single-key body (required[0]).
  - "body_passthrough": POST/PUT where the caller passes a raw `body` dict directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import server
from app import mcp


@dataclass(frozen=True)
class ToolSpec:
    """Declarative description of one Factuplan endpoint as an MCP tool.

    Interface (drives FastMCP schema):
      name: tool __name__.
      sig:  exact original parameter list as source text (no parens).
      doc:  exact original docstring.

    Behavior (drives the runtime request):
      method:  HTTP verb.
      path:    path template; {name} placeholders are filled from args.
      mode:    construction mode (see module docstring).
      query:   ordered query-param argument names (mode="params").
      required: ordered required body-field names.
      optional: ordered optional (drop-none) body-field names.
    """

    name: str
    sig: str
    doc: str
    method: str
    path: str
    mode: str
    query: tuple[str, ...] = ()
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()


async def _dispatch(spec: ToolSpec, args: dict[str, Any]) -> str:
    """Replay spec's original request from the captured call args."""
    path = spec.path.format(**args) if "{" in spec.path else spec.path
    params: dict[str, Any] | None = None
    body: dict[str, Any] | None = None

    if spec.mode == "params":
        params = {k: args[k] for k in spec.query} if spec.query else None
    elif spec.mode == "body":
        body = {k: args[k] for k in spec.required}
        body.update(server._drop_none({k: args[k] for k in spec.optional}))
    elif spec.mode == "body_literal":
        key = spec.required[0]
        body = {key: args[key]}
    elif spec.mode == "body_passthrough":
        # The tool receives a raw dict parameter; forward it as-is.
        body = args.get("body")
    else:
        raise ValueError(f"Unknown tool mode: {spec.mode!r}")

    kwargs: dict[str, Any] = {}
    if params is not None:
        kwargs["params"] = params
    if body is not None:
        kwargs["body"] = body
    result = await server._request(spec.method, path, **kwargs)
    return server._json(result)


_EXEC_GLOBALS = {"Any": Any}


def build_tool(spec: ToolSpec):
    """Compile, register and return one generated tool fn."""
    src = (
        f"async def {spec.name}({spec.sig}) -> str:\n"
        f"    {spec.doc!r}\n"
        f"    return await __dispatch(__spec, locals())\n"
    )
    ns = dict(_EXEC_GLOBALS)
    ns["__dispatch"] = _dispatch
    ns["__spec"] = spec
    exec(compile(src, f"<tool:{spec.name}>", "exec"), ns)  # nosec B102
    fn = ns[spec.name]
    fn.__doc__ = spec.doc
    fn.__module__ = "tools._registry"
    mcp.tool()(fn)
    return fn


def register_all(specs) -> dict[str, Any]:
    """Build + register every spec; return {name: fn}."""
    built: dict[str, Any] = {}
    for spec in specs:
        built[spec.name] = build_tool(spec)
    return built
