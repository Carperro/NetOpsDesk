# Registro de decisiones — Analizador de gateway y rutas

Este registro contiene decisiones específicas de la herramienta 10. Las decisiones globales se consultan en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md); las propuestas aquí no amplían la autorización para implementar.

## Decisiones aprobadas

### ROUTE-DEC-001 — Diagnóstico local de solo lectura

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** la herramienta analiza configuración del sistema operativo en el que se ejecuta el servidor.
- **Decisión:** no recibe parámetros; consulta gateway predeterminado y rutas IPv4 locales.
- **Motivo:** necesidad de identificar la salida por defecto y revisar rutas del servidor.
- **Consecuencias:** los datos describen el host servidor, no necesariamente el equipo que accede a la interfaz. La herramienta no modifica rutas ni configuración.
- **Aprobación:** solicitud del usuario para documentar la herramienta 10.

### ROUTE-DEC-002 — Endpoint GET sin body

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** exponer `GET /api/v1/tools/route-analyzer/execute`, sin request body.
- **Consecuencias:** no se toman argumentos de comandos desde la solicitud.

### ROUTE-DEC-003 — Runner inyectado y comandos fijos

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** el dominio `netops_desk/route_analyzer.py` recibe un `RouteRunner` y no importa `subprocess`. El adaptador ejecuta `ipconfig` y `route print -4` como listas de argumentos, con `shell=False`, capturando bytes.
- **Motivo:** aislar el dominio y restringir la superficie de ejecución del sistema.
- **Consecuencias:** ningún dato de usuario se incorpora a los comandos; el dominio decodifica con `errors="replace"` y parsea resultados.

### ROUTE-DEC-004 — Parsing resistente a localización

- **Estado:** APROBADA como objetivo por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** identificar gateway mediante las etiquetas `Default Gateway` o `Puerta de enlace predeterminada`, y parsear las filas de `route print -4` estructuralmente, usando tokens y formatos numéricos en vez de depender de encabezados localizados.
- **Consecuencias:** deben conservarse fixtures de salida representativos de Windows en español e inglés; la compatibilidad real por versión/localización queda pendiente de verificación.

### ROUTE-DEC-005 — Límites de ejecución y concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** timeout de 10 segundos por comando y `asyncio.Semaphore(5)` global.
- **Consecuencias:** para que el semáforo asyncio sea global, desplegar con un único worker de Uvicorn. El timeout global para ambos comandos y la conducta ante saturación no se especificaron.

## Pendientes de decisión

### ROUTE-PEND-001 — Selección de gateway cuando hay varias rutas por defecto

Definir la regla de selección, por ejemplo mediante métricas y/o interfaz activa, y cómo se valida contra `ipconfig`. No seleccionar silenciosamente la primera coincidencia.

### ROUTE-PEND-002 — Ausencia de gateway o fallo parcial

Definir si `default_gateway` admite `null`, si se devuelve un error o si se permite una respuesta parcial cuando uno de los comandos falla.

### ROUTE-PEND-003 — Política de errores HTTP

Definir estados y códigos para timeout, fallo de ejecución, salida ilegible o permisos insuficientes; alinear mensajes públicos en español y sobre común del Módulo 2.

### ROUTE-PEND-004 — Saturación y privacidad de respuesta

Definir si el sexto diagnóstico concurrente espera o recibe HTTP 429. Revisar si la respuesta requiere `Cache-Control: no-store` y restricciones de exposición, dado que revela configuración local del servidor.
