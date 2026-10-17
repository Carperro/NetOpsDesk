# Principios y estándares de NetOps Desk

## Principios arquitectónicos

### Modularidad y separación de responsabilidades
- Cada componente tendrá responsabilidades definidas.
- Interfaz, API, lógica de negocio, persistencia e integraciones estarán desacopladas.
- El dominio de cálculo será independiente de FastAPI, del navegador y de la base de datos para ejecutar los cálculos centrales.
- Se evitarán tanto los componentes monolíticos como la fragmentación innecesaria.

### Desarrollo progresivo y dependencias justificadas
- Cada componente se implementará y probará antes de continuar.
- No se incorporarán frameworks ni bibliotecas sin una necesidad técnica concreta.
- Las dependencias serán explícitas y justificadas técnicamente.

### Seguridad por defecto y funcionamiento local
- Autenticación, autorización, validación y manejo de errores se implementarán en el servidor cuando corresponda.
- Las herramientas que no necesiten conectividad externa funcionarán sin Internet.
- Las operaciones específicas del sistema operativo estarán aisladas para facilitar futura adaptación a otros sistemas operativos.

### Trazabilidad y verificabilidad
- Las decisiones importantes y los cambios de arquitectura quedarán documentados.
- Los resultados deberán poder probarse mediante pruebas automatizadas o procedimientos de validación definidos.
- Los errores se comunicarán de forma consistente y no expondrán información sensible.

## Estándares de ingeniería

### Calidad del código
- Utilizar nombres claros y coherentes.
- Aplicar anotaciones de tipos en Python cuando corresponda.
- Mantener funciones y módulos enfocados en una responsabilidad.
- Validar las entradas en los límites del sistema.
- Evitar duplicar reglas de negocio.
- No ocultar errores mediante excepciones genéricas o valores de éxito ficticios.
- No añadir abstracciones sin una justificación concreta.

### Pruebas y validación
- Las pruebas deberán corresponder a requisitos o comportamientos definidos.
- Los cálculos tendrán pruebas de casos normales, límites y entradas inválidas.
- Los servicios podrán probarse sin depender de la interfaz.
- Las pruebas de API comprobarán códigos HTTP, esquemas y errores.
- Las pruebas de persistencia utilizarán una base de datos temporal o aislada cuando corresponda.
- No se considerará terminada una funcionalidad solo porque la interfaz parezca funcionar.

### Documentación y continuidad
- La documentación será suficiente para que otra sesión o agente pueda continuar el proyecto sin depender de conversaciones anteriores.
- Se documentarán requisitos, criterios de aceptación, arquitectura, dependencias, contratos de API, modelos de datos, seguridad, estrategia de pruebas, instrucciones de desarrollo y decisiones arquitectónicas.
- Las decisiones importantes registrarán: identificador, contexto, decisión adoptada, motivo, alternativas consideradas (cuando sea relevante), consecuencias y estado.
- No se mantendrán múltiples documentos como fuentes oficiales contradictorias.

### Consideraciones específicas de IPv4/CIDR (para referencia)
*Nota: Los siguientes puntos son específicos de la herramienta IPv4/CIDR y se documentan en su documentación especializada:*
- Uso posible del módulo `ipaddress` de Python estándar para cálculos de red.
- Formato de mensajes de error de la API: `{"error": "string", "detail": "string"}`.
- Endpoint exacto: `POST /api/v1/tools/ipv4/calculate`.
- Tratamiento propuesto de prefijos /31 y /32 en cuanto a hosts utilizables (ver documentación específica).
- Validación opcional de que la IP proporcionada debe ser la dirección de red para el prefijo dado.