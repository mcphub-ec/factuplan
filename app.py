"""
Factuplan FastMCP application instance.

Separated so that server.py (the runtime entry-point) and tools/* can both
import `mcp` without circular dependencies.
"""

import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "factuplan",
    host=os.getenv("MCP_HOST", "0.0.0.0"),  # nosec: B104
    instructions=(
        "MCP server for Factuplan REST API v1, a certified electronic invoicing "
        "solution for Ecuador (SRI). "
        "Provides tools to issue and list electronic invoices, manage clients, "
        "products, categories, price types, taxes, warehouses, establishments, "
        "emission points, and companies. "
        "Requires FACTUPLAN_API_KEY environment variable. "
        "TYPICAL FLOW: listar_puntos_emision → emitir_factura with puntoEmisionId. "
        "Payment method codes (metodo_pago): 01=Cash/other, 16=Debit card, "
        "19=Credit card, 20=Bank transfer. "
        "ID type codes (tipo_identificacion): 04=RUC, 05=Cedula, 06=Passport, "
        "07=Final consumer (identificacion='9999999999999'), 08=Foreign ID."
    ),
)
