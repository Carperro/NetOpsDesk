# Arquitectura del Planificador VLSM

## Componentes

- **Dominio:** `src/netops_desk/vlsm.py` implementa `calculate_vlsm`. Utiliza la biblioteca estándar `ipaddress` para interpretar redes y `math` para calcular el tamaño del bloque. No depende de FastAPI ni del navegador.
- **Modelos de API:** `src/netops_desk/api/models/vlsm.py` define los modelos Pydantic de entrada (`VlsmInput`, `VlsmRequirement`) y de salida (`VlsmOutput`, `VlsmAllocated`, `VlsmRemaining`).
- **Router:** `src/netops_desk/api/routes/vlsm.py` declara `/api/v1/tools/vlsm`, adapta los requerimientos Pydantic a diccionarios para el dominio y traduce `DomainError` a una respuesta HTTP 400.
- **Aplicación:** `src/netops_desk/api/main.py` registra el router y sirve la página en `/tools/vlsm`.
- **Frontend:** `src/netops_desk/static/tools/vlsm.html` contiene la página y `src/netops_desk/static/js/vlsm.js` gestiona el formulario, las filas dinámicas de requerimientos, la llamada a la API y la presentación de resultados.
- **Estilos:** la página carga `src/netops_desk/static/css/vlsm.css` junto con los estilos compartidos.

El cálculo de asignaciones permanece en el dominio. El frontend recopila los datos y muestra la respuesta de la API; no calcula prefijos por su cuenta.

## Flujo

1. La persona ingresa una red CIDR y uno o más requerimientos.
2. El navegador envía `POST /api/v1/tools/vlsm/calculate` con JSON.
3. FastAPI valida el cuerpo mediante `VlsmInput` y sus modelos anidados.
4. El router convierte la lista de requerimientos a diccionarios y llama a `calculate_vlsm`.
5. La respuesta se valida y serializa con `VlsmOutput`; el frontend presenta las subredes y el espacio restante.

## Manejo de errores observado

Los errores de validación Pydantic responden HTTP 422. El router convierte `DomainError` en `HTTPException` con estado 400 y el detalle del dominio. El handler HTTP compartido asigna actualmente el código público `invalid_json` a las respuestas 400; esa asignación es el comportamiento actual del handler común, no una clasificación específica de VLSM.
