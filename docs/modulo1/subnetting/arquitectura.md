# Arquitectura de Subnetting IPv4

Las convenciones HTTP compartidas del Módulo 1 están en [`../api-contracts.md`](../api-contracts.md).

## Componentes

- **Dominio:** `src/netops_desk/subnetting.py` implementa `calculate_subnets_by_count` y `calculate_subnets_by_hosts` usando la biblioteca estándar `ipaddress`. No depende de FastAPI ni del navegador.
- **Modelos API:** `src/netops_desk/api/models/subnetting.py` define `SubnettingByCountInput`, `SubnettingByHostsInput`, `SubnetResult` y `SubnettingOutput`. `api/models/__init__.py` reexporta estos modelos.
- **Rutas API:** `src/netops_desk/api/routes/subnetting.py` declara el router `/api/v1/tools/subnetting`, transforma los resultados del dominio a `SubnetResult` y expone las operaciones por cantidad y por hosts.
- **Aplicación:** `src/netops_desk/api/main.py` registra el router y sirve la página de la herramienta en `/tools/subnetting`.
- **Frontend:** `src/netops_desk/static/tools/subnetting.html` contiene la interfaz; `static/js/subnetting.js` valida entradas en el navegador, llama a la API y presenta los resultados. Usa los estilos comunes de alerta en `static/css/styles.css` y estilos propios en `static/css/subnetting.css`.

El sidebar se inyecta desde `static/js/sidebar.js`; `static/js/common.js` contiene comportamiento compartido. El navegador no ejecuta los cálculos de red: los solicita a la API.

## Manejo de errores observado

Las rutas capturan `ValueError` del dominio y lo convierten en `HTTPException(400)`. El handler compartido responde `bad_request` para esos errores HTTP 400; reserva `invalid_json` para el error de lectura del cuerpo que reconoce expresamente. El contrato común aprobado establece HTTP 422 para errores de entrada y dominio, por lo que la ruta actual tiene una brecha de implementación pendiente.

## Pruebas

`tests/test_subnetting.py` verifica el dominio. No hay pruebas HTTP específicas de las dos rutas ni pruebas estáticas enfocadas en la página y el JavaScript de Subnetting. El alcance y los límites de esa cobertura se describen en `requisitos.md`.
