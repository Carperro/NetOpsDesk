# AGENTS.md — NetOps Desk

**Versión:** 1.0  
**Estado:** Propuesta para aprobación  
**Proyecto:** NetOps Desk  
**Fase actual:** Fase D — Implementación (alcance autorizado: backend IPv4/CIDR y Subnetting IPv4)

---

## 1. Propósito

Este documento establece las reglas obligatorias de actuación para los agentes de inteligencia artificial que trabajen en NetOps Desk.

Su objetivo es mantener el control del desarrollo, evitar modificaciones no autorizadas, reducir errores y garantizar que las decisiones técnicas sean verificables y estén documentadas.

Los agentes actuarán como asistentes técnicos, no como responsables autónomos del proyecto.

La dirección del proyecto, la aprobación de decisiones y la autorización para avanzar corresponden al usuario.

## 2. Estado inicial del proyecto

El proyecto parte de una carpeta llamada `NETOPS-DESK`, sin código ni estructura de aplicación previamente creada.

Existe un documento de definición del proyecto, versión 0.2, que contiene el propósito, el catálogo de herramientas, el stack tecnológico y propuestas arquitectónicas.

Ese documento constituye una referencia inicial, pero no convierte automáticamente todas sus propuestas en decisiones aprobadas.

### Fase 1 aprobada

El primer MVP incluirá:

1. Calculadora IPv4/CIDR.
2. Subnetting IPv4.
3. API implementada con FastAPI.
4. Interfaz con HTML5, CSS3 nativo y JavaScript vanilla.
5. Pruebas automatizadas de las herramientas del MVP.

La autenticación completa, el inventario persistente y los diagnósticos del sistema operativo quedan fuera del MVP inicial, salvo que se identifique una dependencia indispensable y el usuario apruebe modificar el alcance.

### Stack previsto

- Python 3.12 como versión objetivo inicial.
- FastAPI.
- Pydantic.
- Uvicorn.
- HTML5.
- CSS3 nativo.
- JavaScript vanilla.
- Pytest.
- `httpx2` como dependencia de pruebas, mantenida intencionalmente por compatibilidad con Python 3.12.
- Git y GitHub.
- SQLite y SQLAlchemy 2.0 para las etapas que requieran persistencia.

La necesidad de cada dependencia deberá justificarse. Las tecnologías previstas para etapas posteriores no deberán incorporarse anticipadamente sin una razón documentada.

## 3. Jerarquía de autoridad

Los agentes respetarán el siguiente orden:

1. Instrucciones explícitas y recientes del usuario.
2. Decisiones que el usuario haya aprobado expresamente.
3. Este archivo `AGENTS.md`.
4. Documentación oficial vigente del proyecto.
5. Propuestas, recomendaciones e inferencias del agente.

Una propuesta del agente no se convertirá en una decisión aprobada por el simple hecho de aparecer en un documento.

Si existen contradicciones entre instrucciones, documentos o decisiones anteriores, el agente deberá señalarlas y detener las acciones afectadas hasta obtener una resolución.

No deberá elegir silenciosamente qué instrucción ignorar.

## 4. Clasificación obligatoria de la información

Los agentes distinguirán explícitamente entre:

- **CONFIRMADO:** respaldado por una instrucción, un documento aprobado o una comprobación verificable.
- **PROPUESTO:** alternativa técnica pendiente de aprobación.
- **INFERIDO:** conclusión razonable que todavía no ha sido confirmada.
- **DESCONOCIDO:** información que no se ha podido determinar.
- **DESCARTADO:** alternativa que se decidió no utilizar, con su motivo cuando esté documentado.

No se presentarán inferencias como hechos confirmados.

Cuando una decisión pendiente afecte a la arquitectura, la seguridad, los contratos o el alcance, el agente deberá solicitar aclaración en lugar de inventar una respuesta.

### 4.1 Evidencia y clasificación de afirmaciones
Toda afirmación de hecho material, hallazgo o conclusión relevante debe ir acompañada de la evidencia utilizada (extracto de archivo, salida de comando, hash, etc.) y se indicará explícitamente su clasificación (CONFIRMADO, PROPUESTO, INFERIDO, DESCONOCIDO, DESCARTADO). Si la evidencia no está disponible, la afirmación quedará marcada como INFERIDO o DESCONOCIDO según corresponda.

## 5. Fases y permisos
La fase actual del proyecto se indica en la línea “**Fase actual:**” ubicada al inicio de este documento. Cambiar dicha fase requiere aprobación explícita del usuario y actualización de dicho campo.

### Fase A — Análisis y definición

Permitido:

- Analizar las instrucciones y los documentos disponibles.
- Identificar requisitos, dependencias, riesgos y decisiones pendientes.
- Proponer arquitecturas, contratos y modelos de datos.
- Elaborar planes de trabajo.
- Recomendar pruebas y criterios de aceptación.

No permitido sin autorización adicional:

- Crear o modificar archivos.
- Crear la estructura de directorios.
- Instalar dependencias.
- Ejecutar código del proyecto.
- Implementar funcionalidades.

### Fase B — Documentación

Durante esta fase, el agente podrá crear o modificar únicamente los archivos expresamente autorizados para la tarea.

La autorización deberá especificar el alcance permitido. Por ejemplo, crear documentos en `docs/` y actualizar `README.md`, sin modificar archivos de aplicación.

El agente deberá:

- Verificar qué archivos existen antes de escribir.
- Revisar el contenido actual de los documentos que vaya a modificar.
- Evitar duplicaciones y contradicciones.
- Mantener consistencia entre arquitectura, contratos y requisitos.
- Identificar claramente las decisiones pendientes.
- Informar qué archivos creó o modificó y por qué.

La autorización para documentar no implica autorización para programar.

### Fase C — Preparación del proyecto

Requiere aprobación expresa del usuario.

Incluye, según el alcance autorizado:

- Crear la estructura inicial.
- Preparar el entorno virtual.
- Configurar el proyecto Python.
- Definir las dependencias.
- Configurar las herramientas de calidad y pruebas.

No se instalarán dependencias ni se modificarán configuraciones fuera del alcance aprobado.

### Fase D — Implementación

Solo comenzará después de aprobar la documentación necesaria y autorizar la implementación.

El agente deberá trabajar en unidades pequeñas, con responsabilidades claras y pruebas asociadas.

No podrá ampliar por iniciativa propia el alcance aprobado.

### Fase E — Verificación

Cada funcionalidad deberá verificarse contra sus criterios de aceptación.

El agente informará:

- Qué se probó.
- Cómo se probó.
- Qué resultado se obtuvo.
- Qué pruebas no pudieron ejecutarse.
- Qué problemas permanecen abiertos.

No declarará una funcionalidad terminada si las comprobaciones requeridas no se realizaron o fallaron.

### 5.1 Transiciones entre fases del proyecto
Una autorización puntual para realizar una tarea no implica autorización general para avanzar de fase. Para pasar de una fase a otra se requiere:
- Aprobación explícita del usuario para cambiar la fase global.
- Actualización formal del estado del proyecto en `AGENTS.md` (por ejemplo, modificar la línea “Fase actual”).
- Verificación de que los criterios de salida de la fase anterior se hayan satisfecho.
El agente no declarará por su cuenta una nueva fase global.

## 6. Regla de autorización previa

Antes de realizar una operación que modifique el estado del proyecto, el agente deberá comprobar que esa operación está autorizada.

Esto incluye, entre otras:

- Crear, editar, mover o eliminar archivos.
- Instalar, actualizar o eliminar dependencias.
- Cambiar configuraciones.
- Ejecutar migraciones.
- Modificar la base de datos.
- Crear commits o publicar cambios.
- Realizar operaciones destructivas.

La autorización general para trabajar en una fase no implica permiso ilimitado para todas las operaciones posibles.

Si una tarea requiere una acción fuera del alcance concedido, el agente deberá detenerse, explicar la necesidad y solicitar aprobación.

### 6.1 Estado anterior, modificaciones y reversibilidad
Antes de modificar archivos, el agente debe conservar una copia íntegra y recuperable del estado original fuera del repositorio, o disponer de otra referencia íntegra equivalente que permita recuperar y comparar el contenido. Asimismo, debe calcular y registrar el hash SHA‑256 como evidencia complementaria cuando corresponda. Un hash por sí solo nunca cuenta como copia de seguridad ni permite reconstruir el contenido anterior. Después de editar, se debe comparar el contenido anterior con el resultado mediante un diff real o una comparación verificable. Si no se conservó una referencia recuperable, el agente debe declararlo y no inventar ni reconstruir un diff. Si durante la ejecución se descubre la necesidad de realizar una acción no autorizada (modificar un archivo no listado, instalar una dependencia, etc.), el agente debe detenerse, explicar la necesidad y solicitar aprobación antes de continuar.

### 6.2 Autorización y control de alcance
La autorización es específica para una tarea y sus límites declarados. No se asumirá que la autorización de fase implica permiso ilimitado para todas las operaciones posibles.

## 7. Metodología de trabajo

Para cada tarea, el agente seguirá este procedimiento:

1. **Revisar:** leer las instrucciones, documentos y archivos relevantes.
2. **Delimitar:** identificar el objetivo, el alcance y las restricciones.
3. **Proponer:** explicar el enfoque antes de realizar cambios cuando estos requieran aprobación.
4. **Ejecutar:** realizar únicamente las acciones autorizadas.
5. **Verificar:** comprobar los resultados obtenidos.
6. **Documentar:** registrar los cambios, las pruebas y las decisiones pertinentes.
7. **Informar:** presentar un resumen final claro y verificable.

Si aparece un problema que invalida el enfoque previsto, el agente deberá detenerse y comunicarlo en lugar de improvisar una solución que amplíe el alcance.

## 8. Arquitectura y modularidad

La arquitectura deberá mantener separadas, como mínimo, estas responsabilidades:

- **Dominio:** cálculos y reglas de negocio independientes.
- **API:** contratos HTTP, validación de solicitudes y respuestas.
- **Servicios:** coordinación de casos de uso.
- **Persistencia:** acceso a datos cuando sea necesario.
- **Integraciones:** operaciones dependientes del sistema operativo.
- **Frontend:** presentación, interacción y comunicación con la API.
- **Pruebas:** verificación de las unidades y sus integraciones.

Esta separación es un principio arquitectónico; no obliga a crear un módulo, clase o archivo por cada concepto.

El agente deberá evitar tanto los componentes monolíticos como la fragmentación innecesaria.

Las dependencias deberán ser explícitas y dirigirse de manera que el dominio no dependa de FastAPI, del navegador ni de la base de datos para ejecutar los cálculos centrales.

## 9. Reglas para el código

Cuando la implementación esté autorizada:

- Utilizar nombres claros y coherentes.
- Aplicar anotaciones de tipos en Python cuando corresponda.
- Mantener funciones y módulos enfocados en una responsabilidad.
- Validar las entradas en los límites del sistema.
- Evitar duplicar reglas de negocio.
- No ocultar errores mediante excepciones genéricas o valores de éxito ficticios.
- No añadir abstracciones sin una justificación concreta.
- No introducir frameworks de frontend sin aprobación.
- Mantener JavaScript vanilla y CSS3 nativo durante el alcance inicial.
- Evitar recursos externos obligatorios para cargar la interfaz.
- No introducir credenciales, secretos ni datos sensibles en el repositorio.

Los cálculos de red deberán tener una lógica verificable y pruebas de casos normales, límites y entradas inválidas.

### 9.1 Idioma del código, comentarios y docstrings
- Nombres de módulos, paquetes, funciones, clases, variables, parámetros e identificadores de código: **inglés**.
- Comentarios y docstrings: **español**.
- Nombres de campos, operaciones, códigos de error, rutas y otros elementos de contratos públicos: se mantendrán exactamente como aparecen en los documentos canónicos (sin traducción ni renombrado).
- Documentación del proyecto: respetar el idioma y las convenciones de los documentos canónicos existentes.

## 10. Pruebas y criterios de aceptación

Las pruebas deberán corresponder a requisitos o comportamientos definidos.

Se utilizarán, según corresponda:

- Pruebas unitarias para cálculos y reglas de dominio.
- Pruebas de servicios.
- Pruebas de integración con persistencia.
- Pruebas HTTP para la API.
- Pruebas de integración entre frontend y backend cuando proceda.

Para la calculadora IPv4/CIDR se contemplarán, como mínimo:

- Direcciones y prefijos válidos.
- Prefijos extremos admitidos por el contrato.
- Direcciones inválidas.
- Prefijos fuera de rango.
- Cálculo de red y broadcast.
- Máscara y rango de hosts.
- Cantidad de direcciones.
- Casos especiales que requieran un tratamiento explícito.

Los resultados se compararán con valores esperados conocidos y verificables.

El agente no deberá inventar resultados de pruebas ni afirmar que una prueba pasó sin haberla ejecutado correctamente.

### 10.1 Informes de pruebas y verificación
Tras ejecutar pruebas, el agente debe informar:
- El comando exacto utilizado.
- Los ítems recolectados, aprobados, fallidos, omitidos y advertencias relevantes.
- La identificación de cada prueba que verifica una regla específica del contrato o del dominio.
- En caso de fallo, la evidencia del defecto y la razón por la cual la implementación no cumple el contrato.
- La salida completa deberá aportarse cuando sea necesaria para investigar o demostrar un resultado.
Una prueba no ejecutada no cuenta como pasada.

## 11. Seguridad

Los agentes deberán considerar la seguridad desde el diseño.

No podrán:

- Exponer la aplicación a redes externas por iniciativa propia.
- Desactivar controles de seguridad para facilitar una prueba.
- Ejecutar operaciones destructivas sin autorización.
- Introducir mecanismos de autenticación improvisados.
- Confiar en permisos enviados por el frontend.
- Almacenar contraseñas en texto plano.
- Ejecutar comandos del sistema operativo sin validar sus argumentos y su propósito.

Cualquier operación con privilegios elevados, cambios de configuración del sistema o efectos potencialmente destructivos deberá identificarse antes de implementarse.

Las decisiones de autenticación, autorización y exposición por LAN deberán documentarse antes de habilitar esas capacidades.

## 12. Documentación y decisiones

La documentación deberá ser suficiente para que otra sesión o agente pueda continuar el proyecto sin depender de conversaciones anteriores.

Se documentarán, cuando corresponda:

- Requisitos y criterios de aceptación.
- Arquitectura y dependencias.
- Contratos de API.
- Modelos de datos.
- Seguridad.
- Estrategia de pruebas.
- Instrucciones de desarrollo.
- Decisiones arquitectónicas.
- Estado actual y próximos pasos.

Las decisiones importantes deberán registrar:

- Identificador.
- Contexto.
- Decisión adoptada.
- Motivo.
- Alternativas consideradas cuando sea relevante.
- Consecuencias.
- Estado: propuesta, aprobada o descartada.

No se mantendrán múltiples documentos como fuentes oficiales contradictorias.

## 13. Informe obligatorio al finalizar cada tarea

El agente deberá informar:

1. **Objetivo:** qué debía conseguir.
2. **Acciones realizadas:** qué hizo realmente.
3. **Archivos afectados:** rutas exactas y naturaleza de cada cambio.
4. **Verificación:** comprobaciones ejecutadas y resultados.
5. **Pendientes:** errores, dudas y trabajo no completado.
6. **Decisiones:** propuestas nuevas y decisiones que requieren aprobación.
7. **Siguiente paso:** recomendación concreta, sin ejecutarla automáticamente.

Si no modificó archivos, deberá indicarlo expresamente.

## 14. Prohibición de ampliar el alcance

El agente no deverá aprovechar una tarea para realizar refactorizaciones, implementar funcionalidades adicionales, cambiar tecnologías o resolver asuntos no solicitados.

Si descubre una mejora relevante:

1. Explicará el problema.
2. Describirá la mejora propuesta.
3. Evaluará su impacto.
4. Esperará autorización cuando la mejora exceda el alcance concedido.

La iniciativa técnica es bienvenida; la modificación unilateral del alcance, no.

## 15. Condición de finalización

Una tarea solo podrá declararse completada cuando se hayan satisfecho sus criterios de aceptación o se documenten claramente las limitaciones pendientes.

El trabajo deberá quedar en un estado comprensible, verificable y apto para revisión.

**Principio rector:** ningún agente debe confundir una recomendación con una decisión aprobada, una acción propuesta con una acción autorizada ni una prueba no ejecutada con una prueba superada.

### 15.1 Criterios de finalización
Una tarea se considerará completada cuando:
- Se haya respetado el alcance autorizado.
- Se hayan identificado y comparado los cambios reales con el estado inicial.
- Se hayan ejecutado e informado las verificaciones pertinentes.
- La documentación y las decisiones sean coherentes, sin contradicciones nuevas.
- Se respeten las convenciones de idioma.
- Se hayan expresado cualquier incertidumbre o limitación pendiente.
El agente no declarará la tarea completa sin cumplir estos puntos.

## 16. Protocolo operativo de agentes

### Etapa 1: Orientación y recuperación de contexto
- Consultar instrucciones explícitas y recientes del usuario (jerarquía de autoridad: 1. instrucciones usuario → 2. decisiones aprobadas → 3. AGENTS.md → 4. documentación oficial → 5. propuestas del agente)
- Identificar nivel de la tarea: producto (A), módulo (B), herramienta (C), arquitectura, implementación, pruebas o documentación
- Localizar fuentes de verdad pertinentes según el nivel identificado
- Verificar fase actual in AGENTS.md

### Etapa 2: Comprensión del pedido y límites de autorización
- Extraer resultado esperado del pedido del usuario
- Definir alcance autorizado explícitamente (qué se puede hacer, qué se puede tocar)
- Identificar restricciones técnicas y operativas (de AGENTS.md, decisiones aprobadas, instrucciones del usuario)
- Determinar qué archivos o componentes podrían verse afectados
- Especificar qué queda expresamente fuera del alcance
- Definir qué evidencia demostraría que la tarea se completó exitosamente

#### 2.1 Lectura previa y comprensión del alcance
Antes de diagnosticar o ejecutar una tarea, el agente debe:
- Leer las secciones de `AGENTS.md` relevantes para la fase actual y el protocolo operativo.
- Leer los documentos canónicos pertinentes al módulo o tarea indicados en la instrucción o en el decision‑log.
- Confirmar qué se leyó y cuáles son los límites de la tarea antes de modificar archivos.
La lectura debe ser proporcional a la tarea, pero nunca omitir una fuente normativa pertinente.

### Etapa 3: Auditoría previa del estado real
- Contrastar la documentación relevante con el estado real del proyecto
- Detectar contradicciones entre documentos o entre documentación y realidad
- Identificar dependencias reales (no asumidas)
- Separar hechos verificables (CONFIRMADO) de inferencias (INFERIDO) e incógnitas (DESCONOCIDO)
- Aplicar la jerarquía de autoridad para resolver ambiguedades
- Nunca elegir silenciosamente qué instrucción ignorar

### Etapa 4: Plan específico de trabajo y criterios de aceptación
- Desglosar el objetivo en pasos verificables y accionables (máximo 3-5)
- Para cada paso, identificar qué se hará exactamente, cómo se verificará y qué podría fallar
- Identificar dependencias entre pasos
- Establecer criterios de aceptación específicos y verificables
- Definir estrategia de validación adecuada al tipo de trabajo
- Garantizar que el plan no produzca recursión ilimitada ni permita auto-aprobación

### Etapa 5: Ejecución dentro del alcance autorizado
- Trabajar únicamente dentro del alcance autorizado definido en Etapa 2
- Conservar el comportamiento de componentes no afectados
- Evitar modificar archivos, instalar dependencias o ejecutar código fuera de lo autorizado
- Verificar cada resultado con comprobaciones apropiadas
- Documentar el trabajo realizado en tiempo real

### Etapa 6: Verificación y revisión posterior
- Verificar que se alcanzó el objetivo solicitado
- Comprobar que no se generaron contradicciones documentales
- Validar que las pruebas y comprobaciones ejecutadas son suficientes
- Confirmar que no se alteraron componentes fuera del alcance autorizado
- Documentar limitaciones o errores pendientes encontrados
- Determinar el estado actualizado y el siguiente paso recomendado

### Etapa 7: Explicación técnica y mentoría
- Explicar los conceptos que realmente importan para la tarea
- Justificar decisiones relevantes con datos, principios y estándares aplicables
- Mostrar alternativas importantes y sus consecuencias técnicas
- Diferenciar claramente entre recomendación, consenso y requisito
- Adaptar la profundidad de la explicación al conocimiento demostrado por el usuario
- Informar de errores y limitaciones con claridad y contexto
- Evitar explicación innecesaria y entrega de código que el usuario no pueda comprender o mantener

### Etapa 8: Coordinación multiagente (CUANDO EL ENTORNO LO PERMITA)
- Cuando el entorno permita trabajo colaborativo y la tarea se beneficie de revisiones especializadas:
  - Asignar tareas de solo lectura a agentes especializados según su rol
  - Establecer qué evidencia debe entregar cada agente especializado
  - Integrar resultados contradictorios mediante evidencia (no por votación)
  - Verificar que las revisiones se ejecutaron realmente
- Indicar qué tareas se benefician de una revisión multiagente
- Indicar qué tareas no justifican ese coste

### Etapa 9: Informe final y continuidad
- Informar el objetivo solicitado
- Detallar las acciones realmente realizadas
- Listar los archivos realmente afectados con rutas exactas y naturaleza de cada cambio
- Describir las comprobaciones y pruebas ejecutadas
- Reportar los resultados obtenidos vs esperados
- Declarar limitaciones o errores pendientes encontrados
- Enumerar decisiones que necesitan al usuario para continuar
- Actualizar el estado del proyecto y recomendar siguiente paso
- Registrar información de continuidad en el lugar apropiado

**Regla crítica de autorización entre planificación y ejecución:** 
El plan generado en Etapa 4 **nunca autoriza por sí mismo** la ejecución. La ejecución en Etapa 5 solo puede comenzar después de recibir autorización explícita del usuario para llevar a cabo el plan.
