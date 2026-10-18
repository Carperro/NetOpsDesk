# Principios y estándares de NetOps Desk

## Principios arquitectónicos

### Modularidad y separación de responsabilidades

- Cada componente tiene responsabilidades definidas.
- Interfaz, API, lógica de negocio, persistencia e integraciones están desacopladas.
- El dominio de cálculo es independiente de FastAPI, del navegador y de la base de datos para ejecutar los cálculos centrales.
- Se evitan tanto los componentes monolíticos como la fragmentación innecesaria.

### Desarrollo progresivo y dependencias justificadas

- Cada componente se implementa y se prueba antes de continuar.
- No se incorporan frameworks ni bibliotecas sin una necesidad técnica concreta.
- Las dependencias son explícitas y están justificadas técnicamente.

### Seguridad por defecto y funcionamiento local

- Las operaciones sensibles se implementan en el servidor, no en el cliente.
- Las herramientas que no necesiten conectividad externa funcionan sin Internet.
- Las operaciones específicas del sistema operativo están aisladas para facilitar su futura adaptación a otros sistemas operativos.
- Los datos no confiables se presentan en la interfaz sin interpretarlos accidentalmente como marcado o código ejecutable.

### Trazabilidad y verificabilidad

- Las decisiones importantes y los cambios de arquitectura quedan documentados.
- Los resultados se prueban mediante pruebas automatizadas o procedimientos de validación definidos.
- Los errores se comunican de forma consistente y no exponen información sensible.

## Estándares de ingeniería

### Calidad del código

- Nombres claros y coherentes.
- Anotaciones de tipos en Python cuando corresponda.
- Funciones y módulos enfocados en una responsabilidad.
- Validación de entradas en las capas pertinentes; la validación de interfaz no sustituye las garantías del servidor ni los invariantes del dominio.
- Sin duplicación de reglas de negocio.
- Sin ocultar errores mediante excepciones genéricas o valores de éxito ficticios.
- Sin abstracciones sin justificación concreta.

### Pruebas y validación

- Las pruebas corresponden a requisitos o comportamientos definidos.
- Los cálculos tienen pruebas de casos normales, límites y entradas inválidas.
- Los servicios pueden probarse sin depender de la interfaz.
- Las pruebas de API comprueban códigos HTTP, esquemas y errores.
- Las pruebas de persistencia utilizan una base de datos temporal o aislada cuando corresponda.
- Una funcionalidad no se considera terminada solo porque la interfaz parezca funcionar.

### Documentación y continuidad

- La documentación es suficiente para que otra sesión o agente continúe el proyecto sin depender de conversaciones anteriores.
- Se documentan requisitos, criterios de aceptación, arquitectura, dependencias, contratos de API, modelos de datos, seguridad, estrategia de pruebas, instrucciones de desarrollo y decisiones arquitectónicas.
- Las decisiones importantes registran: identificador, contexto, decisión, motivo, alternativas consideradas (cuando sea relevante), consecuencias y estado.
- No se mantienen múltiples documentos como fuentes oficiales contradictorias.
