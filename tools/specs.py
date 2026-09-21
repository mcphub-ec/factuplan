"""Spec table for the data-driven Factuplan tool registry.

All 23 tools expressed as ToolSpec entries. The factory in tools/_registry.py
builds and registers each one on import, preserving the original signatures and
docstrings byte-for-byte so FastMCP produces identical JSON schemas.
"""

from typing import Any

from tools._registry import ToolSpec, register_all


SPECS = [
    # ═══════════════════════════════════════════════════════════════════════
    # FACTURAS  –  /facturas
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_facturas",
        sig="",
        doc=(
            "Retrieve all issued electronic invoices and their SRI authorization status.\n\n"
            "    Use this tool to list all invoices in Factuplan with their current status\n"
            "    (authorized, pending, rejected). No parameters required.\n\n"
            "    RETURNS:\n"
            "      List of invoice objects. Each item includes: id, numero, fecha,\n"
            "      cliente, total, estado (Autorizado/Pendiente/Rechazado).\n"
            "    "
        ),
        method="GET",
        path="/facturas",
        mode="params",
    ),
    ToolSpec(
        name="emitir_factura",
        sig=(
            "cliente_identificacion: str, "
            "cliente_razon_social: str, "
            "items: list[dict[str, Any]], "
            "punto_emision_id: str | None = None, "
            "metodo_pago: str = \"01\", "
            "fecha_emision: str | None = None, "
            "cliente_email: str | None = None, "
            "cliente_direccion: str | None = None, "
            "cliente_telefono: str | None = None"
        ),
        doc=(
            "⚠️ MUTATION — Issue an electronic invoice to the SRI via Factuplan — POST /facturas.\n\n"
            "    Use this tool to generate and submit an electronic invoice (factura electrónica).\n"
            "    The invoice is signed and sent to the SRI automatically.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      cliente_identificacion (str): Customer cedula, RUC, or passport number.\n"
            "                                    For final consumer use \"9999999999999\".\n"
            "      cliente_razon_social (str): Customer full name or company name.\n"
            "      items (list[dict]): List of billed items. Each item object:\n"
            "                          {\n"
            "                            \"descripcion\": \"Product name\",  # REQUIRED\n"
            "                            \"cantidad\": 2.0,                # REQUIRED: quantity\n"
            "                            \"precioUnitario\": 10.50,        # REQUIRED: unit price without VAT\n"
            "                            \"codigoPrincipal\": \"PROD-001\",  # Optional: product code\n"
            "                            \"descuento\": 0.0               # Optional: item discount\n"
            "                          }\n\n"
            "    OPTIONAL PARAMETERS:\n"
            "      punto_emision_id (str): Emission point ID. Get available IDs with listar_puntos_emision.\n"
            "      metodo_pago (str, default=\"01\"): SRI payment method code.\n"
            "                                        Valid values: \"01\"=Cash/other, \"16\"=Debit card,\n"
            "                                        \"19\"=Credit card, \"20\"=Bank transfer.\n"
            "      fecha_emision (str): Issue date in YYYY-MM-DD format. Defaults to today.\n"
            "      cliente_email (str): Customer email for document delivery.\n"
            "      cliente_direccion (str): Customer address.\n"
            "      cliente_telefono (str): Customer phone number.\n\n"
            "    RETURNS:\n"
            "      Dict with: id, numero (invoice number), claveAcceso (49-digit SRI key),\n"
            "      estado (authorization status), and fecha_autorizacion.\n"
            "    "
        ),
        method="POST",
        path="/facturas",
        mode="body",
        required=("cliente_identificacion", "cliente_razon_social", "items", "metodo_pago"),
        optional=("punto_emision_id", "fecha_emision", "cliente_email", "cliente_direccion", "cliente_telefono"),
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # CLIENTES  –  /clients
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_clientes",
        sig="",
        doc=(
            "Retrieve all customers registered in Factuplan.\n\n"
            "    Use this tool to search for existing customers before creating a new one,\n"
            "    or to get customer IDs for other operations.\n\n"
            "    RETURNS:\n"
            "      List of customer objects with: id, tipoIdentificacion, identificacion,\n"
            "      razonSocial, email, telefono, direccion.\n"
            "    "
        ),
        method="GET",
        path="/clients",
        mode="params",
    ),
    ToolSpec(
        name="obtener_cliente",
        sig="id: str",
        doc=(
            "Get details of a specific customer by their Factuplan ID.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Unique customer ID in Factuplan. Example: \"clt_abc123\"\n\n"
            "    RETURNS:\n"
            "      Customer object with: id, tipoIdentificacion, identificacion,\n"
            "      razonSocial, email, telefono, direccion.\n"
            "    "
        ),
        method="GET",
        path="/clients/{id}",
        mode="params",
    ),
    ToolSpec(
        name="crear_cliente",
        sig=(
            "tipo_identificacion: str, "
            "identificacion: str, "
            "razon_social: str, "
            "email: str | None = None, "
            "direccion: str | None = None, "
            "telefono: str | None = None"
        ),
        doc=(
            "⚠️ MUTATION — Create a new customer in Factuplan — POST /clients.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      tipo_identificacion (str): SRI document type code.\n"
            "                                  Valid values: \"04\"=RUC, \"05\"=Cedula,\n"
            "                                  \"06\"=Passport, \"07\"=Final consumer,\n"
            "                                  \"08\"=Foreign ID.\n"
            "      identificacion (str): ID number, max 13 characters. Example: \"0912345678\"\n"
            "      razon_social (str): Customer full name or company name.\n\n"
            "    OPTIONAL PARAMETERS:\n"
            "      email (str): Customer email for invoice delivery.\n"
            "      direccion (str): Customer address.\n"
            "      telefono (str): Customer phone number.\n\n"
            "    RETURNS:\n"
            "      Dict with the created customer id and all fields.\n"
            "    "
        ),
        method="POST",
        path="/clients",
        mode="body",
        required=("tipo_identificacion", "identificacion", "razon_social"),
        optional=("email", "direccion", "telefono"),
    ),
    ToolSpec(
        name="actualizar_cliente",
        sig=(
            "id: str, "
            "tipo_identificacion: str, "
            "identificacion: str, "
            "razon_social: str, "
            "email: str | None = None, "
            "direccion: str | None = None, "
            "telefono: str | None = None"
        ),
        doc=(
            "⚠️ MUTATION — Update an existing customer in Factuplan — PUT /clients/{id}.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Customer ID to update. Example: \"clt_abc123\"\n"
            "      tipo_identificacion (str): SRI document type code (04=RUC, 05=Cedula, etc.).\n"
            "      identificacion (str): ID number. Example: \"0912345678\"\n"
            "      razon_social (str): Customer full name or company name.\n\n"
            "    OPTIONAL PARAMETERS:\n"
            "      email (str): Updated email.\n"
            "      direccion (str): Updated address.\n"
            "      telefono (str): Updated phone.\n\n"
            "    RETURNS:\n"
            "      Dict with updated customer data.\n"
            "    "
        ),
        method="PUT",
        path="/clients/{id}",
        mode="body",
        required=("tipo_identificacion", "identificacion", "razon_social"),
        optional=("email", "direccion", "telefono"),
    ),
    ToolSpec(
        name="eliminar_cliente",
        sig="id: str",
        doc=(
            "⚠️ IRREVERSIBLE MUTATION — Delete a customer from Factuplan — DELETE /clients/{id}.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Unique customer ID to delete. Example: \"clt_abc123\"\n\n"
            "    RETURNS:\n"
            "      Confirmation of deletion.\n"
            "    "
        ),
        method="DELETE",
        path="/clients/{id}",
        mode="params",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # PRODUCTOS  –  /products
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_productos",
        sig="",
        doc=(
            "Retrieve all products and services registered in Factuplan.\n\n"
            "    Use this tool to find product IDs before creating an invoice or\n"
            "    to verify existing catalog entries.\n\n"
            "    RETURNS:\n"
            "      List of product objects with: id, codigoPrincipal, nombre,\n"
            "      precioUnitario, tipoImpuestoId, categoriaId.\n"
            "    "
        ),
        method="GET",
        path="/products",
        mode="params",
    ),
    ToolSpec(
        name="obtener_producto",
        sig="id: str",
        doc=(
            "Get details of a specific product by its Factuplan ID.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Unique product ID in Factuplan. Example: \"prd_xyz789\"\n\n"
            "    RETURNS:\n"
            "      Product object with: id, codigoPrincipal, nombre, precioUnitario,\n"
            "      tipoImpuestoId, categoriaId, descripcion.\n"
            "    "
        ),
        method="GET",
        path="/products/{id}",
        mode="params",
    ),
    ToolSpec(
        name="crear_producto",
        sig=(
            "codigo_principal: str, "
            "nombre: str, "
            "precio_unitario: float, "
            "codigo_auxiliar: str | None = None, "
            "descripcion: str | None = None, "
            "tipo_impuesto_id: str | None = None, "
            "categoria_id: str | None = None"
        ),
        doc=(
            "⚠️ MUTATION — Create a new product or service in Factuplan — POST /products.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      codigo_principal (str): Unique product code. Example: \"PROD-001\"\n"
            "      nombre (str): Product or service name. Example: \"Web Hosting Monthly\"\n"
            "      precio_unitario (float): Base unit price WITHOUT VAT. Example: 15.00\n\n"
            "    OPTIONAL PARAMETERS:\n"
            "      codigo_auxiliar (str): Auxiliary or barcode. Example: \"BAR-001\"\n"
            "      descripcion (str): Detailed product description.\n"
            "      tipo_impuesto_id (str): Tax type ID (e.g. VAT 0%, VAT 15%, ICE).\n"
            "                              Get available IDs with listar_impuestos.\n"
            "      categoria_id (str): Product category ID.\n"
            "                          Get available IDs with listar_categorias.\n\n"
            "    RETURNS:\n"
            "      Dict with created product id and all fields.\n"
            "    "
        ),
        method="POST",
        path="/products",
        mode="body",
        required=("codigo_principal", "nombre", "precio_unitario"),
        optional=("codigo_auxiliar", "descripcion", "tipo_impuesto_id", "categoria_id"),
    ),
    ToolSpec(
        name="actualizar_producto",
        sig=(
            "id: str, "
            "codigo_principal: str, "
            "nombre: str, "
            "precio_unitario: float, "
            "codigo_auxiliar: str | None = None, "
            "descripcion: str | None = None, "
            "tipo_impuesto_id: str | None = None, "
            "categoria_id: str | None = None"
        ),
        doc=(
            "⚠️ MUTATION — Update an existing product in Factuplan — PUT /products/{id}.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Product ID to update. Example: \"prd_xyz789\"\n"
            "      codigo_principal (str): Product code. Example: \"PROD-001\"\n"
            "      nombre (str): Product name.\n"
            "      precio_unitario (float): Unit price WITHOUT VAT.\n\n"
            "    OPTIONAL PARAMETERS:\n"
            "      codigo_auxiliar, descripcion, tipo_impuesto_id, categoria_id.\n"
            "      (Same optional fields as crear_producto.)\n\n"
            "    RETURNS:\n"
            "      Dict with updated product data.\n"
            "    "
        ),
        method="PUT",
        path="/products/{id}",
        mode="body",
        required=("codigo_principal", "nombre", "precio_unitario"),
        optional=("codigo_auxiliar", "descripcion", "tipo_impuesto_id", "categoria_id"),
    ),
    ToolSpec(
        name="eliminar_producto",
        sig="id: str",
        doc=(
            "⚠️ IRREVERSIBLE MUTATION — Delete a product from Factuplan — DELETE /products/{id}.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      id (str): Unique product ID to delete. Example: \"prd_xyz789\"\n\n"
            "    RETURNS:\n"
            "      Confirmation of deletion.\n"
            "    "
        ),
        method="DELETE",
        path="/products/{id}",
        mode="params",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # CATEGORÍAS  –  /categories
    # ═══════════════════���═══════════════════════════════════════════════════
    ToolSpec(
        name="listar_categorias",
        sig="",
        doc=(
            "Retrieve all product categories configured in Factuplan.\n\n"
            "    Use this tool to get category IDs before creating or updating products.\n\n"
            "    RETURNS:\n"
            "      List of category objects with: id, nombre.\n"
            "    "
        ),
        method="GET",
        path="/categories",
        mode="params",
    ),
    ToolSpec(
        name="crear_categoria",
        sig="nombre: str",
        doc=(
            "⚠️ MUTATION — Create a new product category in Factuplan — POST /categories.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      nombre (str): Category name. Example: \"Services\", \"Materials\", \"Hardware\"\n\n"
            "    RETURNS:\n"
            "      Dict with the created category id and nombre.\n"
            "    "
        ),
        method="POST",
        path="/categories",
        mode="body_literal",
        required=("nombre",),
    ),
    # ════════════════════════════��══════════════════════════════════════════
    # TIPOS DE PRECIO  –  /price-types
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_tipos_precio",
        sig="",
        doc=(
            "Retrieve all price types configured in Factuplan (e.g. wholesale, retail).\n\n"
            "    Use this tool to get priceType IDs before assigning prices to products.\n\n"
            "    RETURNS:\n"
            "      List of price type objects with: id, nombre.\n"
            "    "
        ),
        method="GET",
        path="/price-types",
        mode="params",
    ),
    ToolSpec(
        name="crear_tipo_precio",
        sig="body: dict[str, Any]",
        doc=(
            "⚠️ MUTATION — Create a new price type in Factuplan — POST /price-types.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      body (dict): Price type object. Refer to Factuplan API docs for required fields.\n"
            "                   Typically includes: {\"nombre\": \"Wholesale\"}\n\n"
            "    RETURNS:\n"
            "      Dict with created price type data.\n"
            "    "
        ),
        method="POST",
        path="/price-types",
        mode="body_passthrough",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # PRECIOS DE PRODUCTO  –  /product-prices
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_precios_producto",
        sig="",
        doc=(
            "Retrieve all prices assigned to products in Factuplan.\n\n"
            "    RETURNS:\n"
            "      List of product-price objects with: id, productId, priceTypeId, precio.\n"
            "    "
        ),
        method="GET",
        path="/product-prices",
        mode="params",
    ),
    ToolSpec(
        name="crear_precio_producto",
        sig="body: dict[str, Any]",
        doc=(
            "⚠️ MUTATION — Assign a price to a product under a price type — POST /product-prices.\n\n"
            "    REQUIRED PARAMETERS:\n"
            "      body (dict): Price assignment object. Refer to Factuplan API docs.\n"
            "                   Typically includes: {\"productId\": \"...\", \"priceTypeId\": \"...\", \"precio\": 15.00}\n\n"
            "    RETURNS:\n"
            "      Dict with created price assignment data.\n"
            "    "
        ),
        method="POST",
        path="/product-prices",
        mode="body_passthrough",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # COMPAÑÍAS / ESTABLECIMIENTOS / PUNTOS DE EMISIÓN
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_companias",
        sig="",
        doc=(
            "Retrieve all companies (emisoras) registered in the Factuplan account.\n\n"
            "    RETURNS:\n"
            "      List of company objects with: id, ruc, razonSocial, nombreComercial.\n"
            "    "
        ),
        method="GET",
        path="/companies",
        mode="params",
    ),
    ToolSpec(
        name="listar_establecimientos",
        sig="",
        doc=(
            "Retrieve all establishments (branches) of the company in Factuplan.\n\n"
            "    Establishments are physical locations identified by a 3-digit SRI code.\n"
            "    Use their IDs when querying emission points.\n\n"
            "    RETURNS:\n"
            "      List of establishment objects with: id, codigo (e.g. \"001\"), direccion.\n"
            "    "
        ),
        method="GET",
        path="/establishments",
        mode="params",
    ),
    ToolSpec(
        name="listar_puntos_emision",
        sig="",
        doc=(
            "Retrieve all emission points (cajas/terminals) configured in Factuplan.\n\n"
            "    Emission points identify the specific terminal issuing invoices (3-digit SRI code).\n"
            "    Use the returned IDs as puntoEmisionId when calling emitir_factura.\n\n"
            "    RETURNS:\n"
            "      List of emission point objects with: id, codigo (e.g. \"002\"),\n"
            "      establishmentId, and current sequence number.\n"
            "    "
        ),
        method="GET",
        path="/emission-points",
        mode="params",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # IMPUESTOS  –  /taxes
    # ═══════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="listar_impuestos",
        sig="",
        doc=(
            "Retrieve all configured taxes in Factuplan (VAT 0%, VAT 15%, ICE, etc.).\n\n"
            "    Use this tool to get tipoImpuestoId values needed when creating or\n"
            "    updating products.\n\n"
            "    RETURNS:\n"
            "      List of tax objects with: id, nombre (e.g. \"IVA 15%\"), porcentaje.\n"
            "    "
        ),
        method="GET",
        path="/taxes",
        mode="params",
    ),
    # ═══════════════════════════════════════════════════════════════════════
    # BODEGAS  –  /warehouses
    # ══════════════════��════════════════════════════════════════════════════
    ToolSpec(
        name="listar_bodegas",
        sig="",
        doc=(
            "Retrieve all inventory warehouses configured in Factuplan.\n\n"
            "    RETURNS:\n"
            "      List of warehouse objects with: id, nombre, descripcion.\n"
            "    "
        ),
        method="GET",
        path="/warehouses",
        mode="params",
    ),
]

# Build + register all tools on import.
TOOLS = register_all(SPECS)
