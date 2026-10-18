# SKILLS.md — Guía de trabajo técnico para NetOps Desk

Este documento reúne prácticas de ingeniería para ayudar a los agentes a analizar, diseñar, implementar, revisar y documentar NetOps Desk con rigor. No convierte al agente en experto certificado, no sustituye la consulta de fuentes técnicas vigentes y no otorga autorización para actuar.

## 1. Cómo usar esta guía

1. Leer `AGENTS.md` y aplicar sus instrucciones, jerarquía de autoridad y límites.
2. Leer esta guía para identificar las prácticas relevantes a la tarea.
3. Consultar las decisiones aprobadas y la documentación canónica del producto, módulo y herramienta afectados.
4. Inspeccionar el estado real del repositorio antes de inferir qué está implementado, probado o pendiente.
5. Trabajar solo dentro de la autorización explícita de la tarea y comunicar incertidumbres.

Las competencias descritas aquí son criterios de trabajo y listas de comprobación, no tecnologías ni funcionalidades aprobadas. No hacen falta todas para cada tarea: aplicar las que correspondan y explicar las exclusiones importantes.

## 2. Orientación a fuentes y decisiones

- Tratar las instrucciones recientes del usuario como máxima autoridad, seguidas de las decisiones que haya aprobado, `AGENTS.md`, documentación vigente y propuestas del agente.
- Distinguir **CONFIRMADO**, **PROPUESTO**, **INFERIDO**, **DESCONOCIDO** y **DESCARTADO**. Acompañar los hallazgos materiales con archivo, sección o evidencia verificable.
- Usar el catálogo para identificar las 25 herramientas del MVP y su estado. El MVP queda completo cuando todas se desarrollan e integran con el frontend (DEC-011).
- Documentar progresivamente cada herramienta tras su integración frontend, en su carpeta específica, incluyendo requisitos, arquitectura, contrato y estrategia de pruebas implementada cuando correspondan.
- Consultar el registro de decisiones para contexto y estado. Una propuesta en documentación o en una conversación del agente no es aprobación.
- La existencia de archivos, rutas, pruebas o cambios locales no prueba aprobación, autoría, ejecución exitosa ni autorización para ampliar el alcance.
- Si dos fuentes relevantes discrepan, identificar cuál tiene autoridad, citar la evidencia y detener la acción afectada si no se puede resolver con decisiones ya aprobadas.

## 3. Ingeniería de software y arquitectura

### 3.1 Límites y dependencias

- Mantener las reglas de negocio en lógica de dominio reutilizable desde distintos transportes, como API o una CLI futura.
- Mantener separados dominio, coordinación de casos de uso, transporte HTTP, persistencia, integraciones del sistema operativo e interfaz. La separación expresa dependencias y responsabilidades; no exige crear una capa o archivo por concepto.
- Evitar que los cálculos centrales dependan de FastAPI, del navegador o de una base de datos.
- Introducir abstracciones solo cuando resuelvan una necesidad actual verificable o una variación prevista y aprobada. No diseñar capas especulativas para tecnologías futuras.
- Mantener explícitos los límites de entrada y salida entre componentes; no duplicar reglas de dominio en rutas HTTP o JavaScript.

### 3.2 Diseño y mantenimiento

- Convertir necesidades en requisitos observables y criterios de aceptación antes de diseñar.
- Preferir cambios pequeños, legibles y localizados. Preservar interfaces y comportamiento ajenos al alcance.
- Revisar convenciones del proyecto antes de introducir patrones o dependencias.
- Tratar errores de manera explícita y coherente; no ocultar fallos ni devolver resultados ficticios.
- Considerar límites de tamaño, tiempo y memoria al procesar entradas o generar resultados.
- Cuando una decisión tenga efectos duraderos, registrar contexto, alternativas pertinentes, decisión, motivo, consecuencias y estado en la fuente de decisiones adecuada.

### 3.3 Evolución tecnológica

La arquitectura debe conservar la lógica de negocio suficientemente aislada para permitir evolución futura. CLI, Linux/macOS, framework frontend, TypeScript, preprocesador CSS y base de datos son posibilidades futuras, no autorización para incorporarlos al MVP. Priorizar portabilidad mediante límites claros y dependencias explícitas; crear documentación o adaptadores específicos solo cuando resuelvan una necesidad concreta.

## 4. Redes y cálculo de direccionamiento

- Confirmar el alcance IP de cada herramienta en sus requisitos y contrato. No asumir que una herramienta IPv4 admite IPv6, ni exigir IPv6 a herramientas para las que no sea pertinente.
- Aplicar representaciones y operaciones de direccionamiento de forma exacta: familia IP, prefijo, máscara, red, broadcast cuando aplique, rangos, cantidades y casos límite deben derivarse de un contrato explícito.
- En subnetting, VLSM y solapamiento, definir límites de entrada y tamaño máximo razonable de resultados. Evitar materializar o recorrer colecciones enormes cuando el contrato permita entradas que causen consumo excesivo.
- Distinguir validación sintáctica (dirección o prefijo válido), validación semántica (combinación permitida por la herramienta) y reglas del caso de uso.
- Tratar casos especiales de IPv4 e IPv6 según las reglas y expectativas documentadas; no trasladar supuestos de una familia a otra.
- Usar ejemplos reproducibles con resultados calculados y revisados. No presentar una sugerencia de red o seguridad como requisito del producto sin aprobación.
- Para funciones dependientes de interfaces, rutas o configuración del sistema operativo, separar el cálculo puro del adaptador específico de plataforma y definir claramente permisos y fallos posibles antes de implementarlo.

## 5. API, contratos y validación

- Consultar el contrato canónico antes de cambiar nombres de campos, rutas, códigos de error, estado HTTP o formato de respuesta.
- Mantener los contratos comunes en su fuente compartida y las particularidades en la documentación de la herramienta; evitar copias divergentes.
- Validar entradas en el límite de la API y volver a proteger invariantes del dominio en la lógica de negocio cuando se pueda invocar desde otros transportes.
- Documentar campos obligatorios/opcionales, tipos, restricciones, ejemplos, resultados, errores y estado HTTP.
- Diferenciar errores de sintaxis, validación, dominio, autorización, recursos inexistentes y fallos internos cuando el contrato lo requiera.
- No revelar trazas, secretos, rutas locales o detalles internos en errores públicos.
- Cuando implementación y contrato difieran, registrar la brecha con evidencia; no modificar código ni contrato para hacerlos coincidir sin autorización correspondiente.
- Considerar compatibilidad de clientes: un cambio incompatible requiere decisión y estrategia explícitas.

## 6. Desarrollo web y frontend

- Tratar el navegador como cliente no confiable. La validación de interfaz mejora la experiencia, pero la API y el dominio deben proteger sus propios límites.
- Insertar datos dinámicos en el DOM usando mecanismos de texto y nodos seguros. Usar HTML interpretado solo cuando exista una necesidad concreta, sanitización apropiada y revisión de seguridad.
- Evitar construir selectores, atributos, URLs o fragmentos de HTML a partir de entrada sin validación contextual.
- Mantener accesibilidad básica: etiquetas asociadas a controles, navegación por teclado, foco perceptible, mensajes de error comprensibles y semántica adecuada.
- Representar estados de carga, éxito, error y ausencia de resultados sin confundirlos.
- Mantener la interfaz utilizable sin recursos externos obligatorios salvo decisión aprobada.
- Evitar dependencias de framework o compilación no aprobadas. Seguir las convenciones existentes de HTML, CSS y JavaScript vanilla mientras sean las tecnologías del proyecto.
- Revisar responsividad y presentación para entradas largas y resultados extensos; no inferir compatibilidad visual sin comprobarla.

## 7. Seguridad, privacidad y recursos

- No confiar en permisos, identificadores de rol ni datos de seguridad enviados por el cliente.
- No introducir secretos en código, documentación, logs o respuestas. Evitar registrar datos de red o configuración que puedan ser sensibles si no son necesarios.
- No exponer servicios a interfaces de red externas ni habilitar acceso LAN por iniciativa propia.
- No ejecutar comandos del sistema operativo con argumentos derivados de entradas sin validación, límites y una justificación concreta.
- Considerar inyección, XSS, exposición de información, solicitudes abusivas y agotamiento de CPU/memoria según la superficie real de la tarea.
- Definir límites máximos y errores previsibles para lotes, rangos, listas de subredes y cargas recibidas.
- Tratar integraciones con el sistema operativo como específicas de plataforma, con fallos explícitos, privilegios mínimos y pruebas adecuadas cuando estén autorizadas.
- Para operaciones que dependan de Internet o servicios externos, distinguir explícitamente modo offline, dependencia de conectividad y comportamiento ante indisponibilidad.
- No añadir autenticación, persistencia, permisos elevados o capacidades de red fuera de la autorización y decisiones vigentes.

## 8. Pruebas y verificación

- Derivar pruebas de requisitos y contratos. Cubrir casos normales, límites, entradas inválidas y errores pertinentes.
- Separar pruebas unitarias de dominio, pruebas de servicios, integración de persistencia, pruebas HTTP e integración de interfaz según las fronteras involucradas.
- Para cálculos de red, comparar con resultados esperados conocidos y cubrir límites de prefijo y comportamiento de cada familia IP admitida.
- Probar propiedades o invariantes cuando sean útiles, por ejemplo: pertenencia de direcciones a una red, ausencia de solapamientos en una partición válida y consistencia de cantidades.
- No confundir archivos de prueba existentes con pruebas ejecutadas. Informar el comando exacto y el resultado observado; nunca afirmar que algo pasó si no se ejecutó.
- Ejecutar verificaciones solo cuando la tarea y su autorización lo permitan. Si no se ejecutan, describir qué queda pendiente y qué verificación sería pertinente.
- No instalar paquetes ni iniciar servicios para verificar sin autorización específica.

## 9. Auditoría y revisión técnica

- Delimitar cada hallazgo a una ubicación y comportamiento observables. Registrar evidencia, impacto, clasificación, autoridad relacionada y grado de certeza.
- Distinguir vulnerabilidad confirmada de patrón potencialmente riesgoso; describir precondiciones y efecto posible sin exagerar.
- Revisar rutas de datos desde la entrada hasta la operación sensible y la salida, así como controles y límites existentes.
- Identificar contradicciones entre documentación, contrato, implementación y pruebas sin decidir silenciosamente cuál debe cambiar.
- No declarar un problema corregido por la mera ausencia de una referencia, un test o un resultado estático.
- En auditorías de solo lectura, no alterar archivos ni ejecutar pruebas dinámicas; indicar claramente la evidencia que requeriría autorización posterior.

## 10. Documentación técnica

- Identificar una fuente principal por tema: catálogo para inventario y estado de herramientas; decisiones para aprobaciones; contratos comunes para reglas compartidas de API; carpeta de herramienta para sus requisitos, arquitectura, contrato específico y pruebas implementadas.
- Mantener coherencia sin copiar íntegramente una fuente en varias. Usar referencias claras y actualizar dependencias documentales en la misma tarea autorizada.
- Documentar lo implementado y verificado con precisión temporal. Marcar propuestas y trabajo futuro como tales.
- Usar rutas y comandos que existan; verificar referencias internas cuando se edite documentación.
- Mantener el idioma y las convenciones de los documentos canónicos. En el código, los identificadores van en inglés y comentarios/docstrings en español según `AGENTS.md`.
- No crear documentos por anticipado para herramientas aún no integradas, salvo que el usuario lo solicite o una decisión aprobada lo requiera.

## 11. Compatibilidad y dependencias

- Confirmar versión de Python, dependencias y comandos en los archivos actuales del proyecto antes de documentarlos o cambiarlos.
- No dar por verificada una afirmación de compatibilidad porque aparezca en `pyproject.toml` o en documentación; distinguir declaración de evidencia de ejecución.
- Justificar cada dependencia por una necesidad concreta, superficie de mantenimiento, compatibilidad y alternativas relevantes.
- No actualizar, instalar, retirar ni sustituir dependencias sin autorización.
- Diseñar integraciones de plataforma con límites que permitan aislar diferencias entre Windows, Linux y macOS si y cuando esas plataformas formen parte del alcance.

## 12. Gestión de cambios y entrega

Antes de editar, identificar los archivos autorizados, revisar sus versiones actuales y conservar la referencia original recuperable según `AGENTS.md`. Después, inspeccionar un diff real y verificar que no se alteraron archivos fuera del alcance.

En la entrega final, informar brevemente:

- Objetivo y alcance autorizado.
- Archivos realmente afectados y motivo.
- Evidencia y verificaciones realizadas, incluyendo las que no se ejecutaron.
- Hallazgos, limitaciones e incertidumbres.
- Decisiones que requieren al usuario y siguiente paso recomendado.

No realizar commits, publicaciones, despliegues ni operaciones destructivas sin autorización específica.
