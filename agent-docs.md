# Agent-First Documentation: Factuplan MCP Server

## 1. Contexto General
Servidor MCP para emisión de facturas electrónicas a través del proveedor
Factuplan (Ecuador). Similar a Invoka: usa créditos prepagados.

## 2. Tecnologías Principales
- **FastMCP 3.3.1**.
- **httpx**: Cliente HTTP asíncrono.
- Header `x-api-key` con `FACTUPLAN_API_KEY`.

## 3. Reglas de Negocio
- **Cada comprobante emitido consume un crédito Factuplan**. Confirmar con el usuario.
- IVA Ecuador: 15% por defecto. 0% solo si el producto es explícitamente "Tarifa 0%".
- Identificaciones: CEDULA (10), RUC (13), PASAPORTE, CONSUMIDOR_FINAL (9999999999999).

## 4. Variables de Entorno
- `FACTUPLAN_API_KEY`: Token de autenticación. **Nunca pasar como parámetro de tool**.
- `FACTUPLAN_BASE_URL`: URL base.
- `FACTUPLAN_HTTP_TIMEOUT`: Timeout HTTP.
- `MCP_HOST`, `MCP_PORT`, `MCP_TRANSPORT_MODE`.

## 5. Herramientas Principales (23 totales)
- `emitir_factura`: Emite una factura electrónica.
- `emitir_nota_credito`: Nota de crédito.
- `emitir_retencion`: Comprobante de retención.
- `consultar_estado`: Estado de un comprobante.
- Y 19 más (gestión de productos, clientes, etc).

## 6. Consideraciones de Seguridad
- **IDEMPOTENCIA**: usar el campo `reference` único por operación.
- No loguear `FACTUPLAN_API_KEY` (filtrado automático).
- Filtro de logging redacts RUCs, cédulas, tokens y cards.

## 7. Instrucciones para Edición de Código
- Patrón `@mcp.tool()` con type hints.
- Cliente HTTP centralizado en `_request()`.

## 8. Tests
- Pendiente: añadir cobertura mínima.
