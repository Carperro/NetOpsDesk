# Registro de decisiones — Información de interfaces de red

Este registro contiene decisiones específicas de la herramienta 11 y decisiones aplicables al Módulo 3 expresamente aprobadas para esta tarea. La existencia del documento no implica implementación.

## Decisiones aprobadas

### DEC-017 — Aprobación de `psutil` para información de interfaces

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Alcance:** Herramienta 11 y próximas herramientas del Módulo 3 que necesiten información nativa de interfaces de red, sujeto a justificar su uso concreto.
- **Contexto:** Leer `ipconfig /all` mediante `subprocess` requiere parsear salida textual dependiente del idioma y formato de Windows.
- **Decisión:** Aprobar `psutil` para obtener direcciones, máscara, MAC, estado y velocidad de interfaces mediante `psutil.net_if_addrs()` y `psutil.net_if_stats()` en el runner de infraestructura.
- **Motivo:** Evitar el parseo frágil de `ipconfig` y obtener datos estructurados de interfaces.
- **Alternativas:** Parsear `ipconfig /all` para todos los campos; descartado porque su salida depende de idioma y formato para datos que psutil entrega estructurados.
- **Consecuencias:** `psutil` debe declararse y fijarse en el lockfile al autorizar la preparación/implementación; este pase documental no instala ni añade la dependencia. El dominio no debe depender directamente de psutil. Gateway y DNS son una excepción acotada que se resuelve por IFACE-DEC-005.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 11, 2026-10-20.

### IFACE-DEC-001 — Consulta de solo lectura sin parámetros

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** Exponer información local mediante una operación GET sin parámetros de entrada.
- **Consecuencia:** Los datos corresponden al servidor de NetOps Desk; la operación no modifica interfaces.

### IFACE-DEC-002 — Runner inyectado

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** El dominio `netops_desk/interfaces.py` recibe un `NetworkInterfacesRunner`. El runner usa `psutil.net_if_addrs()` y `psutil.net_if_stats()` para las propiedades de interfaz y construye objetos estructurados; el dominio valida y devuelve el resultado.

### IFACE-DEC-003 — Contrato inicial de campos

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** La respuesta incluye por interfaz `name`, `mac_address`, `ipv4`, `netmask`, `gateway`, `dns_servers`, `is_up` y `speed_mbps`.

### IFACE-DEC-004 — Límite de concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** La capa API usará `asyncio.Semaphore(5)` global con un único worker de Uvicorn.
- **Consecuencias:** No ejecutar varios workers en este despliegue, ya que cada proceso tendría un semáforo independiente. La conducta ante saturación sigue pendiente.

### IFACE-DEC-005 — Gateway y DNS mediante `ipconfig /all`

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** El runner obtiene IP, máscara, MAC, estado y velocidad con psutil; para gateway y servidores DNS ejecuta el comando fijo `ipconfig /all` con `shell=False` y extrae únicamente esos datos mediante regex.
- **Motivo:** satisfacer el alcance del catálogo para gateway/DNS, manteniendo psutil como fuente estructurada de las propiedades de interfaz.
- **Consecuencias:** la salida de `ipconfig /all` requiere asociación por sección de adaptador y consideración de variaciones de idioma. Ningún dato del request entra al comando. El timeout del comando deberá definirse antes de implementar.

### IFACE-DEC-006 — Campos opcionales y velocidad no informada

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** `mac_address`, `ipv4`, `netmask` y `gateway` pueden ser `null`; `dns_servers` es un array que puede estar vacío; `speed_mbps` será `0` si el sistema no informa velocidad.

## Pendientes de decisión

### IFACE-PEND-001 — Cardinalidad de direcciones

Definir qué dirección IPv4 se devuelve cuando una interfaz tiene varias y cómo se selecciona un gateway cuando hay más de uno. La semántica de ausencia y velocidad se cerró en IFACE-DEC-006.

### IFACE-PEND-002 — Saturación del semáforo

Definir si la solicitud adicional espera o recibe HTTP 429; el requisito de un solo worker para que el semáforo sea global está fijado en IFACE-DEC-004.

### IFACE-PEND-003 — Errores y datos parciales

Definir la política de API ante fallos de psutil, una interfaz con datos incompletos o una consulta parcial del sistema.
