# Arquitectura — Visor de caché ARP

> Estado: arquitectura objetivo basada en el alcance aprobado. No describe componentes implementados.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/arp_viewer.py` | Recibir bytes/resultados tipados del runner, decodificar y convertir secciones y entradas a datos estructurados | Biblioteca estándar y `ArpRunner`; no importa `subprocess`, FastAPI ni módulos del navegador |
| Runner/infraestructura | Adaptador por determinar al implementar | Ejecutar `arp -a` con argumentos fijos, `shell=False`, capturar bytes y aplicar timeout de 10 segundos | `subprocess` y sistema operativo |
| Modelos y API | Modelos/ruta por determinar al implementar | Exponer `GET /api/v1/tools/arp-viewer/execute`, coordinar dominio y serializar respuesta | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por determinar | Solicitar y presentar la tabla local | API y recursos locales |
| Pruebas | Archivos por determinar al implementar | Verificar parseo, adaptación de proceso y contrato HTTP | Pytest y dobles de prueba |

## Flujo principal

1. El cliente solicita el endpoint GET sin parámetros ni cuerpo.
2. La ruta intenta adquirir uno de los cinco permisos del `asyncio.Semaphore(5)`; si no hay uno disponible, responde HTTP `429` con `too_many_requests`. El semáforo debe ser global para la aplicación.
3. El runner ejecuta exactamente `arp -a` con `shell=False`, captura stdout como bytes y termina la ejecución si supera 10 segundos.
4. El dominio decodifica con `errors="replace"`, identifica encabezados/secciones de interfaz y reconoce filas que contengan una IP destino, una MAC y un tipo dinámico/estático.
5. El dominio normaliza MAC a minúsculas y reemplaza `:` por `-`; mapea `dinámica`/`dynamic` a `dynamic` y `estática`/`static` a `static`.
6. El dominio asocia cada entrada con la interfaz anunciada por Windows y limita el resultado a un máximo de 500 entradas.
7. La API serializa la respuesta —incluido `entries: []` si no hay entradas— y libera el permiso incluso ante error.

## Límites y errores

- **Validación en interfaz:** no hay campos de usuario que validar; la interfaz solo presenta los datos devueltos.
- **Validación API/dominio:** no se aceptan parámetros para construir el comando. El parser debe validar estructuralmente cada fila antes de emitirla y conservar la asociación con su sección de interfaz.
- **Errores y advertencias:** el fallo del comando y el timeout producen `DomainError(code="execution_failed")`, que el handler global traduce a HTTP `422`; el semáforo agotado produce HTTP `429` con `too_many_requests`. La respuesta HTTP ante salida no parseable sigue pendiente.
- **Recursos y seguridad:** ejecutar una lista fija de argumentos con `shell=False`; no concatenar contenido del request. Decodificar con reemplazo para evitar errores de codificación. El dominio limita el resultado a 500 entradas; un límite de bytes de stdout y la política de selección si hay más de 500 entradas siguen pendientes.

## Estrategia de parseo

- Reconocer encabezados de interfaz como `Interfaz: 192.168.1.33 --- 0x5` y sus variantes localizadas mediante patrones estructurales, no una frase única como fuente exclusiva.
- Interpretar filas únicamente cuando se detecten una dirección IPv4 válida, una dirección MAC de seis octetos y un marcador de tipo reconocido.
- Normalizar el MAC a minúsculas y reemplazar dos puntos por guiones; exponer `entry_type` como `dynamic` o `static`.
- Mapear los marcadores `dinámica` y `dynamic` a `dynamic`; mapear `estática` y `static` a `static`. No se afirma compatibilidad con otras traducciones sin muestras y cobertura explícita.
- Limitar a 500 el número de entradas devueltas. La selección y el orden cuando existan más entradas requieren definición.
- Ignorar o registrar como no reconocidas las filas incompletas; no asociarlas a una interfaz anterior si el parser perdió el límite de sección.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dominio con runner inyectado; consulta fija `arp -a`; salida del runner en bytes; `shell=False`; timeout de 10 segundos; máximo de 500 entradas; normalización de MAC y tipos; semáforo global `asyncio.Semaphore(5)` con HTTP 429 al agotarse; `execution_failed` traducido a HTTP 422 para fallo/timeout.
- **Alternativas descartadas:** aceptar host o filtro en el request; ejecutar comandos construidos con datos de entrada.
- **Dependencias de plataforma/conectividad:** lectura de la caché ARP local de Windows; no consulta hosts externos.
- **Límites que permiten evolución futura:** el dominio queda separado del mecanismo de proceso y puede probarse con bytes de salida simulados; no implica soporte para otros sistemas operativos.

## Pendientes de diseño

- Definir el estado HTTP ante salida sin estructura reconocible y si se clasifica como `execution_failed`.
- Para que el semáforo asyncio sea global entre solicitudes, desplegar un único worker Uvicorn; varios workers tendrían semáforos independientes.
- Establecer un límite de bytes de stdout para evitar materializar una salida anormalmente grande.
- Definir selección y orden de las entradas si el parser encuentra más de 500.
