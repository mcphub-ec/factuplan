"""
Factuplan MCP Server v1
=======================
MCP server for the Factuplan REST API v1 — certified electronic invoicing
platform for Ecuador (SRI).

Technical reference: docs/openapi.yaml
"""

import os
import json
import logging
from typing import Any

from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

# Cargar variables desde el archivo .env
load_dotenv()


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "name":"%(name)s", "message":"%(message)s"}',
)
logger = logging.getLogger("factuplan-mcp")

FACTUPLAN_BASE_URL = os.environ.get(
    "FACTUPLAN_BASE_URL", "https://api.factuplan.com.ec/v1"
)

HTTP_TIMEOUT = float(os.environ.get("FACTUPLAN_HTTP_TIMEOUT", "30"))

mcp = FastMCP(
    "factuplan",
    host="0.0.0.0",
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
    ))

# ---------------------------------------------------------------------------
# Cliente HTTP reutilizable
# ---------------------------------------------------------------------------


def _build_headers() -> dict[str, str]:
    """Build auth headers for a specific account."""
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
    *,    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None) -> dict | list | str:
    """Ejecuta una petición HTTP contra la API de Factuplan y devuelve la respuesta."""
    url = f"{FACTUPLAN_BASE_URL}{path}"
    # Limpiar parámetros vacíos / None
    if params:
        params = {k: v for k, v in params.items() if v is not None and v != ""}

    logger.info("%s %s params=%s", method.upper(), url, params)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.request(
            method,
            url,
            headers=_build_headers(),
            params=params,
            json=body)
        logger.info("Respuesta HTTP %s", resp.status_code)

        if resp.status_code >= 400:
            error_body = resp.text
            return {
                "error": True,
                "status_code": resp.status_code,
                "detail": error_body,
            }

        # Respuesta vacía en 204
        if not resp.text.strip():
            return {"ok": True, "status_code": resp.status_code}

        try:
            return resp.json()
        except Exception:
            return resp.text


# ═══════════════════════════════════════════════════════════════════════════
# MÓDULO TRANSACCIONAL: FACTURAS  –  /facturas
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_facturas() -> str:
    """Retrieve all issued electronic invoices and their SRI authorization status.

    Use this tool to list all invoices in Factuplan with their current status
    (authorized, pending, rejected). No parameters required.

    RETURNS:
      List of invoice objects. Each item includes: id, numero, fecha,
      cliente, total, estado (Autorizado/Pendiente/Rechazado).
    """
    result = await _request("GET", "/facturas")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def emitir_factura(    cliente_identificacion: str,
    cliente_razon_social: str,
    items: list[dict[str, Any]],
    punto_emision_id: str | None = None,
    metodo_pago: str = "01",
    fecha_emision: str | None = None,
    cliente_email: str | None = None,
    cliente_direccion: str | None = None,
    cliente_telefono: str | None = None) -> str:
    """⚠️ MUTATION — Issue an electronic invoice to the SRI via Factuplan — POST /facturas.

    Use this tool to generate and submit an electronic invoice (factura electrónica).
    The invoice is signed and sent to the SRI automatically.

    REQUIRED PARAMETERS:
      cliente_identificacion (str): Customer cedula, RUC, or passport number.
                                    For final consumer use "9999999999999".
      cliente_razon_social (str): Customer full name or company name.
      items (list[dict]): List of billed items. Each item object:
                          {
                            "descripcion": "Product name",  # REQUIRED
                            "cantidad": 2.0,                # REQUIRED: quantity
                            "precioUnitario": 10.50,        # REQUIRED: unit price without VAT
                            "codigoPrincipal": "PROD-001",  # Optional: product code
                            "descuento": 0.0               # Optional: item discount
                          }

    OPTIONAL PARAMETERS:
      punto_emision_id (str): Emission point ID. Get available IDs with listar_puntos_emision.
      metodo_pago (str, default="01"): SRI payment method code.
                                        Valid values: "01"=Cash/other, "16"=Debit card,
                                        "19"=Credit card, "20"=Bank transfer.
      fecha_emision (str): Issue date in YYYY-MM-DD format. Defaults to today.
      cliente_email (str): Customer email for document delivery.
      cliente_direccion (str): Customer address.
      cliente_telefono (str): Customer phone number.

    RETURNS:
      Dict with: id, numero (invoice number), claveAcceso (49-digit SRI key),
      estado (authorization status), and fecha_autorizacion.

    EXAMPLE CALL:
      emitir_factura(
          cliente_identificacion="0912345678", cliente_razon_social="Juan Pérez",
          items=[{"descripcion": "Consulting", "cantidad": 1, "precioUnitario": 100.00}],
          metodo_pago="01"
      )
    """
    cliente: dict[str, Any] = {
        "identificacion": cliente_identificacion,
        "razonSocial": cliente_razon_social,
    }
    if cliente_email is not None:
        cliente["email"] = cliente_email
    if cliente_direccion is not None:
        cliente["direccion"] = cliente_direccion
    if cliente_telefono is not None:
        cliente["telefono"] = cliente_telefono

    body: dict[str, Any] = {
        "cliente": cliente,
        "items": items,
        "metodoPago": metodo_pago,
    }
    if punto_emision_id is not None:
        body["puntoEmisionId"] = punto_emision_id
    if fecha_emision is not None:
        body["fechaEmision"] = fecha_emision

    result = await _request("POST", "/facturas", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CATÁLOGO: CLIENTES  –  /clients
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_clientes() -> str:
    """Retrieve all customers registered in Factuplan.

    Use this tool to search for existing customers before creating a new one,
    or to get customer IDs for other operations.

    RETURNS:
      List of customer objects with: id, tipoIdentificacion, identificacion,
      razonSocial, email, telefono, direccion.
    """
    result = await _request("GET", "/clients")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def obtener_cliente(    id: str
) -> str:
    """Get details of a specific customer by their Factuplan ID.

    REQUIRED PARAMETERS:
      id (str): Unique customer ID in Factuplan. Example: "clt_abc123"

    RETURNS:
      Customer object with: id, tipoIdentificacion, identificacion,
      razonSocial, email, telefono, direccion.
    """
    result = await _request("GET", f"/clients/{id}")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def crear_cliente(    tipo_identificacion: str,
    identificacion: str,
    razon_social: str,
    email: str | None = None,
    direccion: str | None = None,
    telefono: str | None = None) -> str:
    """⚠️ MUTATION — Create a new customer in Factuplan — POST /clients.

    Use this tool to register a customer before issuing an invoice if they are
    not already in the system. The identificacion is the unique customer identifier.

    REQUIRED PARAMETERS:
      tipo_identificacion (str): SRI document type code.
                                  Valid values: "04"=RUC, "05"=Cedula,
                                  "06"=Passport, "07"=Final consumer,
                                  "08"=Foreign ID.
      identificacion (str): ID number, max 13 characters. Example: "0912345678"
      razon_social (str): Customer full name or company name.

    OPTIONAL PARAMETERS:
      email (str): Customer email for invoice delivery.
      direccion (str): Customer address.
      telefono (str): Customer phone number.

    RETURNS:
      Dict with the created customer id and all fields.

    EXAMPLE CALL:
      crear_cliente(tipo_identificacion="05", identificacion="0912345678",
                    razon_social="Juan Pérez", email="juan@example.com")
    """
    body: dict[str, Any] = {
        "tipoIdentificacion": tipo_identificacion,
        "identificacion": identificacion,
        "razonSocial": razon_social,
    }
    if email is not None:
        body["email"] = email
    if direccion is not None:
        body["direccion"] = direccion
    if telefono is not None:
        body["telefono"] = telefono

    result = await _request("POST", "/clients", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def actualizar_cliente(    id: str,
    tipo_identificacion: str,
    identificacion: str,
    razon_social: str,
    email: str | None = None,
    direccion: str | None = None,
    telefono: str | None = None) -> str:
    """⚠️ MUTATION — Update an existing customer in Factuplan — PUT /clients/{id}.

    REQUIRED PARAMETERS:
      id (str): Customer ID to update. Example: "clt_abc123"
      tipo_identificacion (str): SRI document type code (04=RUC, 05=Cedula, 06=Passport, etc.).
      identificacion (str): ID number. Example: "0912345678"
      razon_social (str): Customer full name or company name.

    OPTIONAL PARAMETERS:
      email (str): Updated email.
      direccion (str): Updated address.
      telefono (str): Updated phone.

    RETURNS:
      Dict with updated customer data.
    """
    body: dict[str, Any] = {
        "tipoIdentificacion": tipo_identificacion,
        "identificacion": identificacion,
        "razonSocial": razon_social,
    }
    if email is not None:
        body["email"] = email
    if direccion is not None:
        body["direccion"] = direccion
    if telefono is not None:
        body["telefono"] = telefono

    result = await _request("PUT", f"/clients/{id}", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def eliminar_cliente(    id: str
) -> str:
    """⚠️ IRREVERSIBLE MUTATION — Delete a customer from Factuplan — DELETE /clients/{id}.

    REQUIRED PARAMETERS:
      id (str): Unique customer ID to delete. Example: "clt_abc123"

    RETURNS:
      Confirmation of deletion.
    """
    result = await _request("DELETE", f"/clients/{id}")
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CATÁLOGO: PRODUCTOS  –  /products
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_productos() -> str:
    """Retrieve all products and services registered in Factuplan.

    Use this tool to find product IDs before creating an invoice or
    to verify existing catalog entries.

    RETURNS:
      List of product objects with: id, codigoPrincipal, nombre,
      precioUnitario, tipoImpuestoId, categoriaId.
    """
    result = await _request("GET", "/products")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def obtener_producto(    id: str
) -> str:
    """Get details of a specific product by its Factuplan ID.

    REQUIRED PARAMETERS:
      id (str): Unique product ID in Factuplan. Example: "prd_xyz789"

    RETURNS:
      Product object with: id, codigoPrincipal, nombre, precioUnitario,
      tipoImpuestoId, categoriaId, descripcion.
    """
    result = await _request("GET", f"/products/{id}")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def crear_producto(    codigo_principal: str,
    nombre: str,
    precio_unitario: float,
    codigo_auxiliar: str | None = None,
    descripcion: str | None = None,
    tipo_impuesto_id: str | None = None,
    categoria_id: str | None = None) -> str:
    """⚠️ MUTATION — Create a new product or service in Factuplan — POST /products.

    REQUIRED PARAMETERS:
      codigo_principal (str): Unique product code. Example: "PROD-001"
      nombre (str): Product or service name. Example: "Web Hosting Monthly"
      precio_unitario (float): Base unit price WITHOUT VAT. Example: 15.00

    OPTIONAL PARAMETERS:
      codigo_auxiliar (str): Auxiliary or barcode. Example: "BAR-001"
      descripcion (str): Detailed product description.
      tipo_impuesto_id (str): Tax type ID (e.g. VAT 0%, VAT 15%, ICE).
                              Get available IDs with listar_impuestos.
      categoria_id (str): Product category ID.
                          Get available IDs with listar_categorias.

    RETURNS:
      Dict with created product id and all fields.
    """
    body: dict[str, Any] = {
        "codigoPrincipal": codigo_principal,
        "nombre": nombre,
        "precioUnitario": precio_unitario,
    }
    optionals = {
        "codigoAuxiliar": codigo_auxiliar,
        "descripcion": descripcion,
        "tipoImpuestoId": tipo_impuesto_id,
        "categoriaId": categoria_id,
    }
    for k, v in optionals.items():
        if v is not None:
            body[k] = v

    result = await _request("POST", "/products", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def actualizar_producto(    id: str,
    codigo_principal: str,
    nombre: str,
    precio_unitario: float,
    codigo_auxiliar: str | None = None,
    descripcion: str | None = None,
    tipo_impuesto_id: str | None = None,
    categoria_id: str | None = None) -> str:
    """⚠️ MUTATION — Update an existing product in Factuplan — PUT /products/{id}.

    REQUIRED PARAMETERS:
      id (str): Product ID to update. Example: "prd_xyz789"
      codigo_principal (str): Product code. Example: "PROD-001"
      nombre (str): Product name.
      precio_unitario (float): Unit price WITHOUT VAT.

    OPTIONAL PARAMETERS:
      codigo_auxiliar, descripcion, tipo_impuesto_id, categoria_id.
      (Same optional fields as crear_producto.)

    RETURNS:
      Dict with updated product data.
    """
    body: dict[str, Any] = {
        "codigoPrincipal": codigo_principal,
        "nombre": nombre,
        "precioUnitario": precio_unitario,
    }
    optionals = {
        "codigoAuxiliar": codigo_auxiliar,
        "descripcion": descripcion,
        "tipoImpuestoId": tipo_impuesto_id,
        "categoriaId": categoria_id,
    }
    for k, v in optionals.items():
        if v is not None:
            body[k] = v

    result = await _request("PUT", f"/products/{id}", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def eliminar_producto(    id: str
) -> str:
    """⚠️ IRREVERSIBLE MUTATION — Delete a product from Factuplan — DELETE /products/{id}.

    REQUIRED PARAMETERS:
      id (str): Unique product ID to delete. Example: "prd_xyz789"

    RETURNS:
      Confirmation of deletion.
    """
    result = await _request("DELETE", f"/products/{id}")
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CATÁLOGO: CATEGORÍAS  –  /categories
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_categorias() -> str:
    """Retrieve all product categories configured in Factuplan.

    Use this tool to get category IDs before creating or updating products.

    RETURNS:
      List of category objects with: id, nombre.
    """
    result = await _request("GET", "/categories")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def crear_categoria(    nombre: str
) -> str:
    """⚠️ MUTATION — Create a new product category in Factuplan — POST /categories.

    REQUIRED PARAMETERS:
      nombre (str): Category name. Example: "Services", "Materials", "Hardware"

    RETURNS:
      Dict with the created category id and nombre.
    """
    result = await _request("POST", "/categories", body={"nombre": nombre})
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CATÁLOGO: TIPOS DE PRECIO  –  /price-types
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_tipos_precio() -> str:
    """Retrieve all price types configured in Factuplan (e.g. wholesale, retail).

    Use this tool to get priceType IDs before assigning prices to products.

    RETURNS:
      List of price type objects with: id, nombre.
    """
    result = await _request("GET", "/price-types")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def crear_tipo_precio(    body: dict[str, Any]
) -> str:
    """⚠️ MUTATION — Create a new price type in Factuplan — POST /price-types.

    REQUIRED PARAMETERS:
      body (dict): Price type object. Refer to Factuplan API docs for required fields.
                   Typically includes: {"nombre": "Wholesale"}

    RETURNS:
      Dict with created price type data.
    """
    result = await _request("POST", "/price-types", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CATÁLOGO: PRECIOS DE PRODUCTO  –  /product-prices
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_precios_producto() -> str:
    """Retrieve all prices assigned to products in Factuplan.

    RETURNS:
      List of product-price objects with: id, productId, priceTypeId, precio.
    """
    result = await _request("GET", "/product-prices")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def crear_precio_producto(    body: dict[str, Any]
) -> str:
    """⚠️ MUTATION — Assign a price to a product under a price type — POST /product-prices.

    REQUIRED PARAMETERS:
      body (dict): Price assignment object. Refer to Factuplan API docs.
                   Typically includes: {"productId": "...", "priceTypeId": "...", "precio": 15.00}

    RETURNS:
      Dict with created price assignment data.
    """
    result = await _request("POST", "/product-prices", body=body)
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# ESTRUCTURA DE COMPAÑÍA: COMPAÑÍAS, ESTABLECIMIENTOS, PUNTOS DE EMISIÓN
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_companias() -> str:
    """Retrieve all companies (emisoras) registered in the Factuplan account.

    RETURNS:
      List of company objects with: id, ruc, razonSocial, nombreComercial.
    """
    result = await _request("GET", "/companies")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def listar_establecimientos() -> str:
    """Retrieve all establishments (branches) of the company in Factuplan.

    Establishments are physical locations identified by a 3-digit SRI code.
    Use their IDs when querying emission points.

    RETURNS:
      List of establishment objects with: id, codigo (e.g. "001"), direccion.
    """
    result = await _request("GET", "/establishments")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def listar_puntos_emision() -> str:
    """Retrieve all emission points (cajas/terminals) configured in Factuplan.

    Emission points identify the specific terminal issuing invoices (3-digit SRI code).
    Use the returned IDs as puntoEmisionId when calling emitir_factura.

    RETURNS:
      List of emission point objects with: id, codigo (e.g. "002"),
      establishmentId, and current sequence number.
    """
    result = await _request("GET", "/emission-points")
    return json.dumps(result, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN: IMPUESTOS Y BODEGAS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def listar_impuestos() -> str:
    """Retrieve all configured taxes in Factuplan (VAT 0%, VAT 15%, ICE, etc.).

    Use this tool to get tipoImpuestoId values needed when creating or
    updating products.

    RETURNS:
      List of tax objects with: id, nombre (e.g. "IVA 15%"), porcentaje.
    """
    result = await _request("GET", "/taxes")
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def listar_bodegas() -> str:
    """Retrieve all inventory warehouses configured in Factuplan.

    RETURNS:
      List of warehouse objects with: id, nombre, descripcion.
    """
    result = await _request("GET", "/warehouses")
    return json.dumps(result, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import uvicorn
    import os

    try:
        import logger
    except ImportError:
        pass

    port = int(os.getenv("MCP_PORT", 8000))
    transport_mode = os.getenv("MCP_TRANSPORT_MODE", "sse").lower()
    print(f"Starting MCP Server on http://0.0.0.0:{port}/mcp ({transport_mode})")
    if transport_mode == "sse":
        app = mcp.sse_app()
    elif transport_mode == "http_stream":
        app = mcp.streamable_http_app()
    else:
        raise ValueError(f"Unknown transport mode: {transport_mode}")
    uvicorn.run(app, host="0.0.0.0", port=port)
