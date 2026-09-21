"""
Factuplan HTTP client module.

Provides _build_headers and _request — the only two functions that touch
the network. All tools import from here so there is a single serialisation
and error-contract path.
"""

from __future__ import annotations

import os
import json
from typing import Any

import httpx

from config import FACTUPLAN_BASE_URL, HTTP_TIMEOUT, logger


def _build_headers() -> dict[str, str]:
    """Build auth headers for the configured Factuplan account."""
    resolved = os.environ.get("FACTUPLAN_API_KEY", "")
    if not resolved:
        raise ValueError(
            "api_key is required for this MCP. Pass it as a tool parameter."
        )
    return {
        "x-api-key": resolved,
        "Content-Type": "application/json",
    }


async def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict | list | str:
    """Execute an HTTP request against the Factuplan API.

    Error contract:
    - HTTP >= 400 → returns {"error": True, "status_code": int, "detail": str}
    - Empty body (204/201) → returns {"ok": True, "status_code": int}
    - Plaintext response → returns {"text": str}
    - JSON response → returns parsed dict or list
    """
    url = f"{FACTUPLAN_BASE_URL}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None and v != ""}

    logger.info("%s %s params=%s", method.upper(), url, params)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.request(
            method,
            url,
            headers=_build_headers(),
            params=params,
            json=body,
        )
    logger.info("Respuesta HTTP %s", resp.status_code)

    if resp.status_code >= 400:
        return {
            "error": True,
            "status_code": resp.status_code,
            "detail": resp.text,
        }

    if not resp.text.strip():
        return {"ok": True, "status_code": resp.status_code}

    try:
        return resp.json()
    except Exception:
        return {"text": resp.text}


def _json(result: Any) -> str:
    """Serialise any tool result to a JSON string (single path, no per-tool dumps)."""
    return json.dumps(result, ensure_ascii=False, default=str)


def _drop_none(d: dict) -> dict:
    """Return a copy of d with None values removed."""
    return {k: v for k, v in d.items() if v is not None}
