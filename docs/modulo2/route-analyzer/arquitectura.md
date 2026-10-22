# Arquitectura — Analizador de gateway y rutas

## Estado

Arquitectura objetivo; no describe componentes implementados. El catálogo mantiene la herramienta 10 pendiente de desarrollo e integración.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/route_analyzer.py` | Recibir un `RouteRunner`, interpretar salidas, identificar gateway y normalizar rutas IPv4 | Interfaz `RouteRunner`, biblioteca estándar para parsing |
| Runner/infraestructura | Adaptador de infraestructura/API | Ejecutar comandos fijos y devolver stdout/stderr como bytes más código de salida | `subprocess`, sistema Windows |
| API | Modelos/ruta de Route Analyzer | Exponer GET sin body, invocar dominio, administrar límite concurrente y traducir resultados | FastAPI/Pydantic, dominio y runner |
| Interfaz | Pendiente de integración | Mostrar gateway y tabla de rutas local | API y recursos locales |
| Pruebas | Archivos de prueba futuros | Probar parser, runner, contrato HTTP y salidas localizadas | Pytest y fixtures de salida |

## Flujo principal

1. El cliente llama `GET /api/v1/tools/route-analyzer/execute` sin parámetros ni body.
2. La ruta adquiere uno de los cinco permisos del semáforo global.
3. El `RouteRunner` ejecuta por separado `ipconfig` y `route print -4` con listas de argumentos, `shell=False`, captura de stdout/stderr en bytes y timeout de 10 segundos por proceso.
4. El dominio recibe los resultados estructurados y decodifica bytes con `errors="replace"`.
5. El parser identifica gateway por las etiquetas `Default Gateway` o `Puerta de enlace predeterminada` considerando estructura de interfaz/valor; extrae filas de ruta por su forma y tokens IPv4/métrica, ignorando cabeceras localizadas.
6. El dominio produce el gateway y las rutas normalizadas; la API los serializa y libera el semáforo incluso ante errores.

## Parsing y datos

- No asumir que todo Windows usa inglés ni español; los dos textos especificados son etiquetas admitidas, no la única base de interpretación.
- `route print -4` imprime una tabla textual con secciones y cabeceras. El parser debe reconocer filas de datos por los campos y sus tipos, no por traducciones exactas de los títulos.
- Una ruta expone `destination`, `netmask`, `gateway`, `interface` y `metric`. La representación de rutas on-link, valores no IPv4, métricas no parseables y filas incompletas debe definirse con fixtures antes de cerrar la implementación.
- `ipconfig` puede enumerar varias interfaces y gateways. Si hay varios gateways candidatos, seleccionar el asociado a la ruta por defecto con la métrica más baja. Si no hay métricas disponibles para compararlos, elegir el primero según el orden en que aparece en la lista de `ipconfig`.
- El resultado corresponde a la máquina que ejecuta el servidor, no al navegador del usuario.

## Seguridad, ejecución y errores

- El runner solo ejecuta los dos comandos fijos autorizados; el request no aporta argumentos a `subprocess`.
- Usar argumentos separados, `shell=False`, capturar bytes y aplicar timeout por comando. No aceptar comandos, banderas ni rutas de ejecutables desde el cliente.
- No registrar ni devolver stderr completo, rutas internas u otros detalles de sistema sin una política explícita.
- La operación no cambia la configuración de red; es de lectura.
- Si falla cualquiera de los comandos o la salida requerida no se puede parsear (por ejemplo, no se encuentra la tabla de rutas), la API responde HTTP `500 Internal Server Error` con el código `execution_failed`. No es un error atribuible al request del usuario.
- La ausencia de gateway sin fallo de comando no está definida como error de parseo y requiere conservar el criterio específico que se decida para ese caso.

## Concurrencia y límites

La API usará `asyncio.Semaphore(5)`. Para que sea global, el despliegue debe ejecutar un solo worker de Uvicorn; varios workers tendrían semáforos independientes. La conducta al agotarse los cinco permisos (espera o HTTP 429) no quedó definida en el pedido.

El timeout se aplica a cada comando por separado. La duración total puede acercarse a 20 segundos si ambos comandos agotan sus respectivos límites; no se especificó un timeout global de request.

## Decisiones estructurales y evolución

- Las dependencias del sistema operativo quedan detrás de `RouteRunner`, para mantener el dominio testeable con un fake y facilitar una sustitución futura.
- La arquitectura objetivo es específica de Windows por los comandos requeridos. Soporte para Linux/macOS no está aprobado por esta tarea.
- No se añaden capas de servicio, persistencia ni abstracciones adicionales sin una necesidad demostrada.

## Referencias

- [Requisitos](requisitos.md).
- [Contrato de API](api-contracts.md).
- [Registro de decisiones](decision-log.md).
- [Arquitectura de Ping](../ping/arquitectura.md), salida localizada y runner aislado.
- [Contrato común del Módulo 1](../../modulo1/api-contracts.md); su extensión al Módulo 2 debe respetar las decisiones transversales vigentes.
