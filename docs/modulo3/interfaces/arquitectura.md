# Arquitectura — Información de interfaces de red

## Estado

Arquitectura objetivo; no describe implementación existente. Los componentes y rutas son destino para una fase de implementación autorizada.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/interfaces.py` | Recibir `NetworkInterfacesRunner`, validar estructura de resultados y devolver datos normalizados | Interfaz del runner; no importa psutil, FastAPI ni el navegador |
| Runner/infraestructura | Adaptador de infraestructura | Combinar datos de psutil y los campos gateway/DNS de `ipconfig /all` en una estructura por interfaz | `psutil`; `subprocess` restringido a un comando fijo |
| API | Ruta GET `/api/v1/tools/interfaces/execute` y modelos | Exponer consulta sin body, aplicar semáforo y serializar respuesta | FastAPI/Pydantic, dominio y runner |
| Interfaz | Pendiente de integración | Mostrar lista y propiedades de interfaces locales | API y recursos locales |
| Pruebas | Archivos a determinar al implementar | Verificar adaptación de datos psutil, dominio y contrato HTTP | Pytest y dobles de prueba |

## Flujo principal

1. El cliente solicita `GET /api/v1/tools/interfaces/execute` sin parámetros ni body.
2. La ruta adquiere uno de los cinco permisos del semáforo.
3. El `NetworkInterfacesRunner` consulta `psutil.net_if_addrs()` y `psutil.net_if_stats()` para obtener MAC, IPv4, máscara, estado y velocidad.
4. El runner ejecuta `ipconfig /all` mediante `subprocess` con `shell=False`, argumentos fijos y captura de bytes; decodifica con `errors="replace"` y extrae únicamente gateway y DNS con patrones estructurales/regex de direcciones.
5. El runner asocia los datos al adaptador correspondiente y construye objetos estructurados con `name`, `mac_address`, `ipv4`, `netmask`, `gateway`, `dns_servers`, `is_up` y `speed_mbps`.
6. El dominio valida la forma y las invariantes acordadas, sin importar psutil ni interpretar texto del sistema operativo.
7. La API devuelve el resultado y libera el semáforo en todos los caminos.

## Adaptación y normalización

- El runner asocia los registros de dirección con las estadísticas por nombre de interfaz.
- La dirección MAC se extrae del tipo de dirección de enlace que informa psutil; IPv4 y máscara se toman de la entrada IPv4 correspondiente.
- Gateway y servidores DNS se obtienen de `ipconfig /all`, parseando solo esos campos y asociándolos a la sección del adaptador correspondiente. No se parsea el volcado completo para sustituir los valores que psutil proporciona.
- `is_up` se deriva del estado de interfaz disponible en las estadísticas.
- `mac_address`, `ipv4`, `netmask` y `gateway` son nulos si no hay valor; `dns_servers` puede ser `[]`; `speed_mbps` vale `0` si el sistema no informa velocidad.
- El parseo de `ipconfig /all` debe contemplar variaciones de idioma y formato, usando etiquetas/secciones locales y patrones de direcciones IP en vez de depender de una frase única.

## Seguridad, recursos y errores

- La operación es de solo lectura, pero expone información de red local (incluidas MAC e IP) del servidor.
- No hay datos del cliente que se incorporen a una operación del sistema operativo.
- No guardar consultas ni resultados en persistencia.
- La respuesta pública no debe exponer excepciones, rutas ni detalles internos de psutil.
- El mapeo de fallos de psutil y el sobre HTTP deben seguir el contrato común que se apruebe para el Módulo 3; no asumir que DEC-012, limitado al Módulo 1, fija automáticamente todos estos casos.

## Concurrencia y evolución

La capa API usará `asyncio.Semaphore(5)` y se desplegará con un solo worker de Uvicorn para que el límite sea global. Varios workers tendrían semáforos independientes. La conducta al agotarse los cinco permisos (espera o HTTP 429) no quedó definida.

La dependencia `psutil` y la ejecución restringida de `ipconfig /all` quedan detrás del runner. Esto reduce el acoplamiento del dominio al sistema operativo y permite sustituir o adaptar las fuentes si cambia la plataforma admitida.

## Decisiones aprobadas y referencias

- [Registro de decisiones](decision-log.md), DEC-017.
- [Catálogo fundacional](../../fundacional/catalogo.md), herramienta 11.
- [Arquitectura de Route Analyzer](../../modulo2/route-analyzer/arquitectura.md), patrón de consulta local y separación de infraestructura.
