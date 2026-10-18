# Arquitectura de Subnetting IPv4

Las convenciones HTTP compartidas del Módulo 1 están en [`../api-contracts.md`](../api-contracts.md).

## Componentes

- **Dominio:** `src/netops_desk/subnetting.py` implementa `calculate_subnets_by_count` y `calculate_subnets_by_hosts` usando la biblioteca estándar `ipaddress`. No depende de FastAPI ni del navegador.
- **Modelos API:** `src/netops_desk/api/models/subnetting.py` define `SubnettingByCountInput`, `SubnettingByHostsInput`, `SubnetResult` y `SubnettingOutput`. `api/models/__init__.py` reexporta estos modelos.
- **Rutas API:** `src/netops_desk/api/routes/subnetting.py` declara el router `/api/v1/tools/subnetting`, transforma los resultados del dominio a `SubnetResult` y expone las operaciones por cantidad y por hosts.
- **Aplicación:** `src/netops_desk/api/main.py` registra el router y sirve la página de la herramienta en `/tools/subnetting`.
- **Frontend:** `src/netops_desk/static/tools/subnetting.html` contiene la interfaz; `static/js/subnetting.js` valida entradas en el navegador, llama a la API y presenta los resultados. Usa los estilos comunes de alerta en `static/css/styles.css` y estilos propios en `static/css/subnetting.css`.

El sidebar se inyecta desde `static/js/sidebar.js`; `static/js/common.js` contiene comportamiento compartido. El navegador no ejecuta los cálculos de red: los solicita a la API.

## Manejo de errores

Las rutas dejan que `DomainError` llegue al handler global, que lo convierte en HTTP 422 con el sobre común. La dependencia compartida `require_json_content_type` rechaza tipos MIME distintos de `application/json` con HTTP 415. Los errores de validación Pydantic también responden 422 con mensajes localizados en español.
## Pruebas

`tests/test_subnetting.py` cubre el dominio y `tests/test_api_subnetting.py` cubre ambos endpoints, errores de esquema y dominio, el contrato común y el tipo de contenido. `tests/test_frontend_static.py` comprueba que las páginas cargan el formateador compartido de errores.