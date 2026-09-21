"""
Factuplan MCP Server — configuration module.

All environment variables and logging setup live here so that _http.py and
tools/* can import them without pulling in the full server namespace.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "name":"%(name)s", "message":"%(message)s"}',
)
logger = logging.getLogger("factuplan-mcp")

# ---------------------------------------------------------------------------
# Runtime flags
# ---------------------------------------------------------------------------

FACTUPLAN_BASE_URL: str = os.environ.get(
    "FACTUPLAN_BASE_URL", "https://api.factuplan.com.ec/v1"
)

HTTP_TIMEOUT: float = float(os.environ.get("FACTUPLAN_HTTP_TIMEOUT", "30"))
