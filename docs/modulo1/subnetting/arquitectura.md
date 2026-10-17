# Arquitectura de Subnetting IPv4

## Componentes

- **Dominio:** `src/netops_desk/subnetting.py` implementa `calculate_subnets_by_count` y `calculate_subnets_by_hosts` usando la biblioteca estándar `ipaddress`. No depende de FastAPI ni del navegador.
- **Modelos API:** `src/netops_desk/api/models/subnetting.py` define `SubnettingByCountInput`, `SubnettingByHostsInput`, `SubnetResult` y `SubnettingOutput`. `api/models/__init__.py` reexporta estos modelos.
- **Rutas API:** `src/netops_desk/api/routes/subnetting.py` declara el router `/api/v1/tools/subnetting`, transforma los resultados del dominio a `SubnetResult` y expone las operaciones por cantidad y por hosts.
- **Aplicación:** `src/netops_desk/api/main.py` registra el router y sirve la página de la herramienta en `/tools/subnetting`.
- **Frontend:** `src/netops_desk/static/tools/subnetting.html` contiene la interfaz; `static/js/subnetting.js` valida entradas en el navegador, llama a la API y presenta los resultados. Usa los estilos comunes de alerta en `static/css/styles.css` y estilos propios en `static/css/subnetting.css`.

El sidebar se inyecta desde `static/js/sidebar.js`; `static/js/common.js` contiene comportamiento compartido. El navegador no ejecuta los cálculos de red: los solicita a la API.

## Manejo de errores observado

Las rutas capturan `ValueError` del dominio y lo convierten en `HTTPException(400)`. El handler compartido de `src/netops_desk/api/exceptions.py` asigna `invalid_json` a cualquier respuesta HTTP 400. En consecuencia, los errores de CIDR o capacidad de Subnetting pueden llevar actualmente ese código aunque no sean errores de JSON. Es una limitación de la implementación observada, no una semántica funcional aprobada para el módulo.

## Pruebas

`tests/test_subnetting.py` verifica el dominio. No hay pruebas HTTP específicas de las dos rutas ni pruebas estáticas enfocadas en la página y el JavaScript de Subnetting. El alcance y los límites de esa cobertura se describen en `requisitos.md`.
