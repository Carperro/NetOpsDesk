# Registro de decisiones — Asistente de configuración IP

Este registro cubre decisiones específicas aprobadas en la solicitud de documentación de la herramienta 12. Los detalles marcados como pendientes no deben tratarse como decisiones.

## Decisiones

### IPCFG-DEC-001 — Generar comandos sin ejecutarlos

- **Estado:** APROBADA para el alcance de la herramienta.
- **Fecha:** 2026-10-20.
- **Contexto:** la herramienta prepara instrucciones de configuración de red, una operación con efectos relevantes.
- **Decisión:** la aplicación genera comandos Windows CMD/Netsh como texto plano y una explicación; la persona decide si los copia y ejecuta manualmente. El servidor no ejecuta comandos ni usa `subprocess`.
- **Motivo:** separar la asistencia informativa de la modificación efectiva de la configuración del sistema.
- **Alternativas:** ejecución automática en el servidor; fuera del alcance aprobado.
- **Consecuencias:** validar estrictamente los argumentos interpolados y mostrar el comando como texto; la interfaz de copiar no debe ejecutar la instrucción.
- **Aprobación:** solicitud explícita del usuario para la herramienta 12.

### IPCFG-DEC-002 — Acciones y campos de entrada

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** se requiere asistir con renovación DHCP, activación DHCP y configuración IPv4 estática.
- **Decisión:** admitir `renew_dhcp`, `set_dhcp`, `set_static` y `set_dns`. Todas requieren `interface_name`; `set_static` requiere además `ip`, `mask` y `gateway`; `set_dns` requiere además `dns_ip`.
- **Motivo:** cubrir las operaciones enumeradas por el usuario.
- **Alternativas:** no registradas.
- **Consecuencias:** el contrato y el dominio validan campos según la acción; la configuración DNS se limita a la acción `set_dns` especificada.
- **Aprobación:** solicitud explícita del usuario para la herramienta 12.

### IPCFG-DEC-003 — No incorporar ejecución del sistema ni operaciones de red

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la herramienta solo compone strings.
- **Decisión:** generación instantánea sin `subprocess` ni consulta al estado de red local.
- **Motivo:** limitar la capacidad de la herramienta a explicar y preparar instrucciones.
- **Alternativas:** no registradas.
- **Consecuencias:** no requiere runner de sistema operativo, timeout de proceso ni semáforo para el alcance definido.
- **Aprobación:** solicitud explícita del usuario para la herramienta 12.

### IPCFG-DEC-004 — Sintaxis de comandos y validación del nombre de interfaz

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** los comandos se copian para ejecución manual en Windows; los valores de solicitud no deben alterar la estructura de la instrucción generada.
- **Decisión:** generar exactamente estas plantillas: `ipconfig /renew "{interface_name}"`; `netsh interface ip set address name="{interface_name}" source=dhcp`; `netsh interface ip set address name="{interface_name}" static {ip} {mask} {gateway}`; y `netsh interface ip set dns name="{interface_name}" static {dns_ip}`. Rechazar `interface_name` si contiene comillas dobles, backticks o caracteres de control.
- **Motivo:** acordar una salida predecible y evitar que el nombre de interfaz cierre su argumento citado o agregue contenido de control.
- **Alternativas:** no registradas.
- **Consecuencias:** validar antes de interpolar; los valores IP también se validan según el campo; el comando se muestra como texto y nunca se ejecuta en el servidor.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### IPCFG-DEC-005 — Códigos de validación de la API

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** errores de acción, campos, formato IP y nombre de interfaz deben ser distinguibles por el cliente.
- **Decisión:** responder HTTP `422` con códigos `invalid_action`, `missing_fields`, `invalid_ip_format` e `invalid_interface_name` para las condiciones correspondientes.
- **Motivo:** ofrecer resultados contractuales estables para entradas que no cumplen las reglas de la operación.
- **Alternativas:** no registradas.
- **Consecuencias:** el contrato común del Módulo 3 debe definir el sobre de error y los estados para errores no cubiertos por esta decisión.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

## Pendientes; no son decisiones aprobadas

- Esquema de respuesta exitosa y tratamiento de campos adicionales.
- Validación semántica de máscara IPv4.
- Sobre JSON común y política de errores distintos de los cuatro errores 422 aprobados.
