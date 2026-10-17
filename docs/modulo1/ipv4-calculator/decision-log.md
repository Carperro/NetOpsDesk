# Registro de decisiones - NetOps Desk MVP

Este documento registra las decisiones aprobadas que son relevantes para el Minimum Viable Product (MVP) de NetOps Desk. Cada decisión incluye un identificador estable, su estado, el contexto en que se tomó, la decisión misma, el motivo y las consecuencias. Las alternativas consideradas se registran solo cuando hay evidencia de que fueron evaluadas explícitamente.

## Decisiones aprobadas

### DEC-001
- **Estado**: APROBADA
- **Contexto**: Definición del alcance del MVP (según la sección "2. Decisiones aprobadas" de la tarea actual).
- **Decisión**: El primer MVP incluirá exclusivamente: calculadora IPv4/CIDR, API con FastAPI, interfaz con HTML5/CSS3/JS vanilla, y pruebas automatizadas del dominio, la API y la integración con la interfaz.
- **Motivo**: Enfocar el esfuerzo inicial en una funcionalidad central verificable que permita validar la arquitectura y el enfoque de desarrollo antes de expandir el alcance.
- **Consecuencias**: 
  - Se pospondrán para etapas posteriores: autenticación, persistencia, inventario, historial de diagnósticos y herramientas de diagnóstico del sistema operativo.
  - El equipo de desarrollo deberá enfocarse en entregar estos cuatro componentes con calidad.
  - Las pruebas deben cubrir no solo el dominio y la API por separado, sino también su integración.
- **Alternativas consideradas**: 
  - Incluir autenticación básica en el MVP (descartada porque complica el inicio y no es esencial para la funcionalidad de cálculo).
  - Incluir persistencia para guardar historial de cálculos (descartada porque añade complejidad de almacenamiento y no es necesaria para verificar el núcleo funcional).

### DEC-002
- **Estado**: APROBADA
- **Contexto**: Restricciones de operación (según la sección "2. Decisiones aprobadas").
- **Decisión**: La aplicación funcionará inicialmente en Windows, el servidor escuchará únicamente en `127.0.0.1`, no se habilitará acceso por LAN en el MVP, la interfaz no dependerá de CDN ni de recursos externos obligatorios, y el cálculo central será independiente de FastAPI, del navegador y de cualquier base de datos.
- **Motivo**: 
  - Limitar la superficie de riesgo y complejidad operativa en la fase inicial.
  - Garantizar que la lógica de negocio pueda ser testeada y evolucionada sin dependencias externas.
  - Asegurar que el MVP pueda ejecutarse en un entorno local sencillo sin configuración de red especial.
- **Consecuencias**:
  - En el MVP, la aplicación solo será accesible desde la máquina donde se ejecuta.
  - Los desarrolladores deberán asegurarse de que el código de dominio no tenga dependencias de frameworks web o de navegador.
  - Cualquier intento de acceder desde otra máquina fallará intencionalmente.
  - La ausencia de CDN y recursos externos obliga a servir todos los assets localmente.
- **Alternativas consideradas**:
  - Escuchar en `0.0.0.0` para permitir acceso LAN desde el inicio (descartado por razones de seguridad y complejidad en la fase inicial).
  - Permitir recursos externos desde CDN para reducir el tamaño del payload inicial (descartado porque introduce dependencia externa y punto de fallo).

### DEC-003
- **Estado**: APROBADA
- **Contexto**: Exclusiones del MVP (según la sección "2. Decisiones aprobadas").
- **Decisión**: Quedan fuera del MVP: autenticación y sesiones de usuario, gestión de usuarios y roles, persistencia de datos, inventario de dispositivos, historial persistente de diagnósticos, y herramientas que ejecuten diagnósticos del sistema operativo. Asimismo, SQLite y SQLAlchemy no se incorporarán al MVP mientras no exista una necesidad aprobada que lo justifique.
- **Motivo**: 
  - Mantener el MVP lo más sencillo posible para permitir una entrega rápida y enfocada en la funcionalidad central.
  - Evitar introducir complejidades que no son directamente relevantes para la calculadora IPv4/CIDR.
  - Asegurar que las decisiones sobre persistencia y autenticación se tomen con información suficiente después de validar el núcleo funcional.
- **Consecuencias**:
  - No se creará ni configurará ninguna base de datos en el MVP.
  - No habrá registro de usuarios ni control de acceso basado en roles.
  - Las herramientas de diagnóstico del sistema operativo (ping, traceroute, etc.) no estarán disponibles en el MVP.
  - El equipo no deberá perder tiempo en configurar ORMs o esquemas de base de datos para el MVP.
- **Alternativas consideradas**:
  - Incluir una base de datos SQLite sencilla para guardar el historial de cálculos (descartado porque no es esencial para el aprendizaje y la verificación del núcleo).
  - Implementar un sistema de roles muy básico (admin/user) para probar el flujo de autenticación (descartado porque añade capas de complejidad innecesarias en esta fase).

### DEC-004
- **Estado**: APROBADA
- **Contexto**: Control del proyecto y restricciones de la fase actual (Documentación).
- **Decisión**: Durante esta fase de documentación, no se permite implementar código, instalar dependencias, modificar la estructura de la aplicación, crear funcionalidades adicionales, ni realizar cambios documentales fuera de los cinco archivos autorizados. Los cambios documentales deberán ser verificables y estar limitados a esta autorización.
- **Motivo**: 
  - Garantizar que el equipo se enfoque en completar la documentación necesaria antes de avanzar a la preparación o implementación.
  - Evitar trabajo adelantado que pueda tener que deshacerse si cambian los requisitos o la arquitectura.
  - Mantener un estado limpio y verificable del proyecto para revisión y aprobación.
- **Consecuencias**:
  - No se crearán archivos de código fuente, configuración ni pruebas ejecutables en esta fase.
  - No se ejecutarán comandos como `pip install`, `python -m venv` o `pytest`.
  - Todos los esfuerzos se concentrarán en crear y revisar los cinco documentos de documentación autorizados.
  - Cualquier desviación de esta restricción requiere aprobación explícita del usuario.
- **Alternativas consideradas**:
  - Permitir la creación de un esqueleto de proyecto estructurado (carpetas vacías) para facilitar la fase posterior (descartado porque crea archivos que no están autorizados y podrían considerarse trabajo adelantado).
  - Allowing the installation of development dependencies in a virtual environment (descartado porque instala archivos y modifica el entorno, lo cual no está autorizado en esta fase).

**Vigencia:** DEC-004 registra restricciones de una fase de documentación anterior. No describe la fase vigente del proyecto ni reemplaza la autorización específica de la tarea actual; la fase global se consulta en `AGENTS.md`.

### DEC-005
- **Estado**: APROBADA
- **Contexto**: Inherente de las fuentes originales (AGENTS.md y README.md) y confirmado en la tarea actual.
- **Decisión**: La arquitectura deberá mantener separadas, como mínimo, las responsabilidades de dominio, API, servicios, persistencia, integraciones, frontend y pruebas. El dominio no dependerá de FastAPI, del navegador ni de la base de datos para ejecutar los cálculos centrales.
- **Motivo**: 
  - Garantizar la modularidad, testeabilidad y mantenibilidad del código a largo plazo.
  - Facilitar la prueba aislada de la lógica de negocio, que es el núcleo del valor de la aplicación.
  - Permitir cambios en una capa sin afectar indebidamente a las otras.
- **Consecuencias**:
  - El código de dominio deberá ser autocontenido y solo depender de la biblioteca estándar de Python (o de dependencias explícitamente aprobadas).
  - La API deberá tratar al dominio como una biblioteca de llamada directa, sin asumir detalles de su implementación más allá de su contrato.
  - El frontend no podrá invocar funciones de dominio directamente; deberá hacerlo a través de la API.
  - Las pruebas podrán verificar el dominio en aislamiento, lo que aumenta la confianza en su corrección.
- **Alternativas consideradas**:
  - Arquitectura monolítica donde todo el código está en una sola capa (descartado porque dificulta las pruebas y el mantenimiento a largo plazo).
  - Arquitectura donde el dominio conoce detalles de la API (por ejemplo, mediante inyección de dependencias de Flask/FastAPI) (descartado porque acopla innecesariamente el dominio al framework web).

### DEC-006
- **Estado**: APROBADA
- **Contexto**: Selección de dependencias para pruebas de API.
- **Decisión**: Utilizar HTTPX exclusivamente como dependencia de pruebas para el TestClient de FastAPI, sin convertirla en dependencia de producción ni del dominio.
- **Motivo**: Permite realizar pruebas de integración con TestClient sin afectar la lógica del dominio ni los requisitos de producción. HTTPX es necesario para TestClient pero no para ejecutar la API en producción.
- **Consecuencias**: 
  - Las pruebas de API podrán utilizar `fastapi.testclient.TestClient` con HTTPX como transporte.
  - El dominio y la API de producción permanecerán independientes de HTTPX.
  - Se debe actualizar `pyproject.toml` para incluir HTTPX en un grupo de dependencias opcionales `test`.
- **Alternativas consideradas**: 
  - Incluir HTTPX como dependencia de producción (descartado porque agrega una dependencia innecesaria para tiempo de ejecución).
  - No utilizar TestClient y probar la API mediante servidor real (descartado porque añade complejidad operativa y requiere un servidor en ejecución durante las pruebas).

**Implementación observada:** `pyproject.toml` declara actualmente la distribución `httpx2` en el grupo opcional `test`; las pruebas importan `fastapi.testclient.TestClient`. Esto describe el estado del repositorio, no acredita una aprobación formal documentada para sustituir la dependencia nombrada originalmente en DEC-006. No hay evidencia en estos archivos para atribuir esa sustitución a una decisión aprobada.

## Reglas recuperadas

Estas reglas proceden del contexto previo del proyecto; no se les atribuye fecha, autor ni aprobación histórica.

- El cálculo directo acepta **cidr** o **address** + **netmask**, mutuamente excluyentes.
- Los bits de host activos se normalizan y producen **host_bits_normalized**.
- Warnings raíz con objetos **{code, message}**.
- Reglas conventional y point-to-point para /31 y /32; fallback conventional más **point_to_point_not_applicable** en otros prefijos.
- Cálculo inverso con **required_hosts >= 1** y **mode**; sin dirección base.
- Campos desconocidos: HTTP 422, código **unknown_field**.
- Clasificación deseada por longest-prefix match; catálogo exacto no disponible.

## Bases aprobadas para preparar el contrato

Autorizadas para preparar esta actualización, sin atribuirles aprobación histórica:

- Excluir **ip** + **prefix** y compatibilidad retroactiva del contrato inicial.
- Permitir **mode** directo opcional, default **conventional**.
- Vocabulario público: **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**, **total_addresses**, **usable_addresses**, **binary**, **warnings**.
- Excluir temporalmente **classification** de la respuesta pública inicial y conservarla como funcionalidad aplazada.

## Decisiones formalizadas en esta actualización

Esta sección registra el contrato preparado en esta actualización para revisión; no atribuye aprobación histórica.

- Respuesta inversa: **required_hosts**, **mode_requested**, **mode_applied**, **prefix**, **total_addresses**, **usable_addresses**, **warnings**; no incluye una red.
- **mode_requested** refleja la entrada. **mode_applied** es point-to-point solo si el prefijo elegido es /31 o /32 bajo ese modo; de otro modo es conventional.
- Evaluar prefijos /32 a /0 y elegir el primero con capacidad efectiva suficiente. La capacidad máxima es 4,294,967,294 en /0; excederla produce 422 **insufficient_capacity**.
- El objeto **binary** directo tiene exactamente seis claves: **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**. Valores en cuatro octetos de ocho bits separados por puntos; null se conserva.
- Cuerpo de error uniforme **{"error": "<code>", "detail": "<message>"}** y orden de validación como define el contrato.
- Retirar explícitamente HTTP 400: no queda una condición contractual diferenciada de las asignadas a 422.

## Bloqueados y aplazados

**classification** no forma parte del response público inicial. La función queda deseada y aplazada hasta verificar el catálogo exacto de 26 asignaciones IANA y el vocabulario de salida. No inventar categorías, prefijos, fechas, autores ni IDs.

---
*Este registro es parte de la documentación obligatoria y debe mantenerse actualizado a lo largo del proyecto. Solo las decisiones marcadas como `APROBADA` deben considerarse vinculantes para el alcance y la arquitectura del MVP.*
