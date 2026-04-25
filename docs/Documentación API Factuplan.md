# **Documentación API Factuplan (Ecuador) para Servidor MCP**

Esta documentación técnica detalla el funcionamiento de la API REST de Factuplan, una solución integral para facturación electrónica en Ecuador que cumple con las normativas del SRI.

## **1\. Entorno y Configuración Base**

* **URL Base:** https://api.factuplan.com.ec/v1  
* **Formato de datos:** JSON. Todas las peticiones deben incluir Content-Type: application/json.

## **2\. Autenticación y API Key (¡Crítico\!)**

La API de Factuplan utiliza llaves estáticas (API Keys) obtenidas desde el panel de desarrollador.

Para acceder a la API, es **obligatorio** incluir la API Key en el encabezado de TODAS las solicitudes. Factuplan soporta dos formatos, siendo x-api-key el estándar documentado:

**Header Requerido:**

x-api-key: \<SU\_API\_KEY\_AQUI\>

*(Nota alternativa: En ciertos endpoints legacy también se admite Authorization: Bearer \<API\_KEY\>)*

## **3\. Arquitectura de Endpoints y Recursos Principales**

Factuplan utiliza una estructura RESTful estándar. Los endpoints base soportan operaciones CRUD completas (GET para listar, POST para crear, PUT para actualizar y DELETE para eliminar usando el ID del recurso).

### **Catálogos del Sistema (CRUD Completo)**

La API estructura sus catálogos principales mayormente en inglés. Tu agente MCP debe exponer herramientas (Tools) para interactuar con estos listados:

* **Compañías (/companies):** Información de las empresas emisoras.  
* **Establecimientos (/establishments):** Sucursales o locales físicos (Ej: 001).  
* **Puntos de Emisión (/emission-points):** Cajas o puntos específicos de emisión (Ej: 002).  
* **Bodegas (/warehouses):** Gestión del inventario físico.  
* **Clientes (/clients):** Directorio de clientes/compradores (Cédula/RUC, Razón Social, Email).  
* **Categorías (/categories):** Organización de productos por familias.  
* **Productos (/products):** Gestión de bienes y servicios facturables.  
* **Impuestos (/taxes):** Configuración de tasas (IVA 15%, IVA 0%, ICE).  
* **Tipos de Precios (/price-types):** Modalidades (mayorista, minorista).  
* **Precios de Productos (/product-prices):** Asignación de precios a productos.

### **Módulo Transaccional: Facturas Electrónicas**

* **Endpoint:** /facturas  
* Este es el endpoint más importante de la plataforma. Recibe la estructura transaccional para generar el XML, firmarlo y enviarlo al SRI.

**Payload básico esperado para POST /facturas:**

{  
  "cliente": {  
    "identificacion": "1234567890001",  
    "razonSocial": "Empresa Demo S.A.",  
    "email": "contacto@demo.com"  
  },  
  "items": \[  
    {  
      "descripcion": "Servicio de Consultoría",  
      "cantidad": 1,  
      "precioUnitario": 100.00  
    }  
  \],  
  "puntoEmisionId": "ID\_DEL\_PUNTO\_DE\_EMISION",  
  "metodoPago": "01"  
}

## **4\. Respuestas HTTP (Status Codes)**

* **200 OK:** Petición procesada correctamente. Retorna arrays (para listas) u objetos JSON.  
* **201 Created:** Recurso (Factura, Producto, Cliente) creado exitosamente.  
* **401 Unauthorized:** Falta el header x-api-key o la clave es incorrecta.  
* **404 Not Found:** La ruta o el ID del recurso consultado no existe.  
* **422 Unprocessable Entity:** Errores de validación (Ej: RUC inválido, RUC no registrado, campos faltantes).