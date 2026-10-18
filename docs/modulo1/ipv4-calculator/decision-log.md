# Registro de decisiones - NetOps Desk MVP

Este documento registra las decisiones aprobadas relevantes para el MVP de NetOps Desk. Cada decisión incluye un identificador estable, su estado, el contexto en que se tomó, la decisión misma, el motivo y las consecuencias. Las alternativas consideradas se registran solo cuando hay evidencia de que fueron evaluadas explícitamente.

> **Vigencia del registro global:** DEC-011, DEC-012 y DEC-013 se mantienen aquí como parte de su historial de origen en IPv4. Desde el 2026-10-18, su copia canónica para decisiones transversales está en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md), junto con DEC-014. Las decisiones específicas de la calculadora IPv4 y las entradas históricas permanecen en este archivo.

## Decisiones aprobadas

### DEC-001

- **Estado**: APROBADA
- **Contexto**: Definición del alcance del MVP.
- **Decisión**: El primer MVP incluirá exclusivamente: calculadora IPv4/CIDR, API con FastAPI, interfaz con HTML5/CSS3/JS vanilla, y pruebas automatizadas del dominio, la API y la integración con la interfaz.
- **Motivo**: Enfocar el esfuerzo inicial en una funcionalidad central verificable que permita validar la arquitectura y el enfoque de desarrollo antes de expandir el alcance.
- **Consecuencias**:
  - Se posponen para etapas posteriores: autenticación, persistencia, inventario, historial de diagnósticos y herramientas de diagnóstico del sistema operativo.
  - El desarrollo se enfoca en entregar estos cuatro componentes con calidad.
  - Las pruebas deben cubrir no solo el dominio y la API por separado, sino también su integración.
- **Alternativas consideradas**:
  - Incluir autenticación básica en el MVP (descartada: complica el inicio y no es esencial para la funcionalidad de cálculo).
  - Incluir persistencia para guardar historial de cálculos (descartada: añade complejidad de almacenamiento y no es necesaria para verificar el núcleo funcional).
- **Vigencia**: la exclusividad de la herramienta 1 quedó sustituida por DEC-009; las demás decisiones de alcance de esta entrada permanecen vigentes.

### DEC-002

- **Estado**: APROBADA
- **Contexto**: Restricciones de operación.
- **Decisión**: La aplicación funcionará inicialmente en Windows, el servidor escuchará únicamente en `127.0.0.1`, no se habilitará acceso por LAN en el MVP, la interfaz no dependerá de CDN ni de recursos externos obligatorios, y el cálculo central será independiente de FastAPI, del navegador y de cualquier base de datos.
- **Motivo**:
  - Limitar la superficie de riesgo y complejidad operativa en la fase inicial.
  - Garantizar que la lógica de negocio pueda ser testeada y evolucionada sin dependencias externas.
  - Asegurar que el MVP pueda ejecutarse en un entorno local sencillo sin configuración de red especial.
- **Consecuencias**:
  - En el MVP, la aplicación solo es accesible desde la máquina donde se ejecuta.
  - El código de dominio no debe tener dependencias de frameworks web ni de navegador.
  - Cualquier intento de acceder desde otra máquina falla intencionalmente.
  - La ausencia de CDN y recursos externos obliga a servir todos los assets localmente.
- **Alternativas consideradas**:
  - Escuchar en `0.0.0.0` para permitir acceso LAN desde el inicio (descartado: seguridad y complejidad en la fase inicial).
  - Permitir recursos externos desde CDN para reducir el tamaño del payload inicial (descartado: introduce dependencia externa y punto de fallo).

### DEC-003

- **Estado**: APROBADA
- **Contexto**: Exclusiones del MVP.
- **Decisión**: Quedan fuera del MVP: autenticación y sesiones de usuario, gestión de usuarios y roles, persistencia de datos, inventario de dispositivos, historial persistente de diagnósticos, y herramientas que ejecuten diagnósticos del sistema operativo. SQLite y SQLAlchemy no se incorporan al MVP mientras no exista una necesidad aprobada que lo justifique.
- **Motivo**:
  - Mantener el MVP lo más sencillo posible para permitir una entrega rápida y enfocada en la funcionalidad central.
  - Evitar introducir complejidades que no son directamente relevantes para la calculadora IPv4/CIDR.
  - Asegurar que las decisiones sobre persistencia y autenticación se tomen con información suficiente después de validar el núcleo funcional.
- **Consecuencias**:
  - No se crea ni configura ninguna base de datos en el MVP.
  - No hay registro de usuarios ni control de acceso basado en roles.
  - Las herramientas de diagnóstico del sistema operativo (ping, traceroute, etc.) no están disponibles en el MVP.
  - El equipo no debe perder tiempo en configurar ORMs o esquemas de base de datos para el MVP.
- **Alternativas consideradas**:
  - Incluir una base de datos SQLite sencilla para guardar el historial de cálculos (descartado: no es esencial para el aprendizaje y la verificación del núcleo).
  - Implementar un sistema de roles muy básico (admin/user) para probar el flujo de autenticación (descartado: añade capas de complejidad innecesarias en esta fase).

### DEC-004

- **Estado**: APROBADA
- **Contexto**: Control del proyecto durante la fase de documentación.
- **Decisión**: Durante la fase de documentación no se permite implementar código, instalar dependencias, modificar la estructura de la aplicación, crear funcionalidades adicionales, ni realizar cambios documentales fuera de los archivos autorizados. Los cambios documentales deben ser verificables y estar limitados a esa autorización.
- **Motivo**:
  - Garantizar que el equipo se enfoque en completar la documentación necesaria antes de avanzar a la preparación o implementación.
  - Evitar trabajo adelantado que pueda tener que deshacerse si cambian los requisitos o la arquitectura.
  - Mantener un estado limpio y verificable del proyecto para revisión y aprobación.
- **Consecuencias**:
  - No se crean archivos de código fuente, configuración ni pruebas ejecutables durante la fase de documentación.
  - No se ejecutan comandos como `pip install`, `python -m venv` o `pytest` durante esa fase.
  - El esfuerzo se concentra en crear y revisar los documentos autorizados.
  - Cualquier desviación requiere aprobación explícita.
- **Alternativas consideradas**:
  - Permitir la creación de un esqueleto de proyecto estructurado (carpetas vacías) para facilitar la fase posterior (descartado: crea archivos no autorizados que podrían considerarse trabajo adelantado).
  - Permitir la instalación de dependencias de desarrollo en un entorno virtual (descartado: instala archivos y modifica el entorno, lo cual no está autorizado en esa fase).
- **Vigencia**: DEC-004 registra restricciones de una fase de documentación anterior. No describe la fase vigente del proyecto.

### DEC-005

- **Estado**: APROBADA
- **Contexto**: Principios de arquitectura.
- **Decisión**: La arquitectura mantiene separadas, como mínimo, las responsabilidades de dominio, API, servicios, persistencia, integraciones, frontend y pruebas. El dominio no depende de FastAPI, del navegador ni de la base de datos para ejecutar los cálculos centrales.
- **Motivo**:
  - Garantizar la modularidad, testeabilidad y mantenibilidad del código a largo plazo.
  - Facilitar la prueba aislada de la lógica de negocio, que es el núcleo del valor de la aplicación.
  - Permitir cambios en una capa sin afectar indebidamente a las otras.
- **Consecuencias**:
  - El código de dominio es autocontenido y solo depende de la biblioteca estándar de Python (o de dependencias explícitamente aprobadas).
  - La API trata al dominio como una biblioteca de llamada directa, sin asumir detalles de su implementación más allá de su contrato.
  - El frontend no invoca funciones de dominio directamente; lo hace a través de la API.
  - Las pruebas pueden verificar el dominio en aislamiento, lo que aumenta la confianza en su corrección.
- **Alternativas consideradas**:
  - Arquitectura monolítica donde todo el código está en una sola capa (descartada: dificulta las pruebas y el mantenimiento a largo plazo).
  - Arquitectura donde el dominio conoce detalles de la API (por ejemplo, mediante inyección de dependencias de Flask/FastAPI) (descartada: acopla innecesariamente el dominio al framework web).

### DEC-006

- **Estado**: APROBADA
- **Contexto**: Selección de dependencias para pruebas de API.
- **Decisión**: Utilizar HTTPX exclusivamente como dependencia de pruebas para el `TestClient` de FastAPI, sin convertirla en dependencia de producción ni del dominio.
- **Motivo**: Permite realizar pruebas de integración con `TestClient` sin afectar la lógica del dominio ni los requisitos de producción. HTTPX es necesario para `TestClient` pero no para ejecutar la API en producción.
- **Consecuencias**:
  - Las pruebas de API pueden utilizar `fastapi.testclient.TestClient` con HTTPX como transporte.
  - El dominio y la API de producción permanecen independientes de HTTPX.
  - `pyproject.toml` incluye la dependencia en el grupo opcional `test`.
- **Alternativas consideradas**:
  - Incluir HTTPX como dependencia de producción (descartado: agrega una dependencia innecesaria para tiempo de ejecución).
  - No utilizar `TestClient` y probar la API mediante servidor real (descartado: añade complejidad operativa y requiere un servidor en ejecución durante las pruebas).

### DEC-007

- **Estado**: APROBADA
- **Contexto**: Verificación del contrato contra la implementación real tras el refactor del backend.
- **Decisión**: Se mantienen **dos códigos de error distintos** para errores relacionados con el cuerpo de la petición:
  - **HTTP 400 `invalid_json`**: errores de lectura o decodificación del cuerpo crudo (bytes UTF-8 inválidos, fallo al leer el cuerpo). El cuerpo no se puede procesar como JSON.
  - **HTTP 422 `invalid_json`**: errores de sintaxis JSON detectados por la validación de Pydantic. El cuerpo se pudo leer pero no es JSON sintácticamente válido.
- **Motivo**: Es el comportamiento real de FastAPI combinado con la capa de excepciones del proyecto. La distinción es útil: 400 indica "no pude procesar el cuerpo crudo", 422 indica "el cuerpo es JSON válido pero no cumple la estructura esperada".
- **Consecuencias**:
  - Se deroga cualquier decisión previa que retiraba HTTP 400 del contrato.
  - `api-contracts.md` documenta ambos casos en su tabla de errores.
  - Las pruebas cubren explícitamente el caso de bytes UTF-8 inválidos que produce 400.
- **Alternativas consideradas**:
  - Mapear todo a 422 (descartado: pierde información diagnóstica).
  - Mapear todo a 400 (descartado: contraintuitivo para errores de validación estructural).

### DEC-008

- **Estado**: APROBADA
- **Contexto**: Sustitución de `httpx` por `httpx2` en el grupo `test`.
- **Decisión**: El grupo opcional `test` de `pyproject.toml` declara la distribución `httpx2` en lugar de `httpx`. Las pruebas siguen usando `fastapi.testclient.TestClient`; no importan directamente `httpx` ni `httpx2`.
- **Motivo**: Se mantiene `httpx2` intencionalmente por compatibilidad con Python 3.12 y con `TestClient`. La migración también responde a la advertencia de deprecación observada en Starlette.
- **Consecuencias**:
  - La suite de pruebas corre sin advertencias de deprecación.
  - `DEC-006` queda parcialmente sustituida en cuanto al nombre del paquete, pero se mantiene vigente en su intención: la dependencia es **solo de pruebas**, no de producción ni del dominio.
- **Alternativas consideradas**:
  - Mantener `httpx` y silenciar la advertencia con `filterwarnings` (descartado: pospone la migración sin resolver la causa).
  - Eliminar la dependencia y no usar `TestClient` (descartado: pierde cobertura de integración HTTP).

### DEC-009

- **Estado**: APROBADA
- **Contexto**: Ampliación oficial del MVP para incorporar la segunda herramienta del Módulo 1.
- **Decisión**: El MVP incluye Subnetting IPv4 además de la Calculadora IPv4/CIDR. Esta decisión sustituye únicamente la exclusividad de herramienta indicada en DEC-001; las demás exclusiones aprobadas se mantienen.
- **Motivo**: El usuario autorizó expresamente incluir e implementar Subnetting IPv4 en el MVP.
- **Consecuencias**:
  - El catálogo y la visión del Módulo 1 identifican las herramientas 1 y 2 como parte del MVP.
  - Subnetting mantiene documentación de requisitos, arquitectura, contrato API y decisiones propia.
  - La aprobación de alcance no equivale a una afirmación de que cada regla esté probada de extremo a extremo.

### DEC-010

- **Estado**: APROBADA
- **Contexto**: Ampliación oficial del MVP para incluir la tercera herramienta del Módulo 1.
- **Decisión**: El MVP incluye el Planificador VLSM además de la Calculadora IPv4/CIDR y Subnetting IPv4. Esta ampliación no altera las exclusiones restantes del MVP.
- **Motivo**: El usuario autorizó expresamente la implementación de la Herramienta 3 y solicitó actualizar la documentación para reflejar su disponibilidad.
- **Consecuencias**:
  - El catálogo y la visión del Módulo 1 identifican las herramientas 1, 2 y 3 como parte del MVP.
  - VLSM mantiene documentación funcional, arquitectónica, de API y de decisiones en `docs/modulo1/vlsm/`.
  - Las decisiones técnicas específicas de VLSM se registran en `docs/modulo1/vlsm/decision-log.md`.

### DEC-011

- **Estado**: APROBADA
- **Contexto**: El alcance del MVP se amplía desde las tres primeras herramientas del Módulo 1 a las 25 herramientas del catálogo oficial.
- **Decisión**: Las 25 herramientas de `docs/fundacional/catalogo.md` forman parte del MVP. El MVP no se considera terminado hasta que las 25 herramientas estén desarrolladas e integradas con la interfaz frontend. El desarrollo y la documentación avanzan progresivamente por herramienta; la documentación de funcionamiento, arquitectura y estrategia de pruebas se completa al terminar la integración frontend de cada herramienta.
- **Motivo**: Decisión expresa del usuario.
- **Vigencia y alcance**:
  - Esta decisión amplía DEC-009 y DEC-010 y sustituye cualquier límite de alcance del MVP que las restrinja a las herramientas 1, 2 o 3.
  - En lo que contradiga la inclusión de las 25 herramientas, sustituye las exclusiones de DEC-003 relativas a herramientas de diagnóstico del sistema operativo, inventario de dispositivos, IPAM, historial de diagnósticos y persistencia necesaria para esas herramientas.
  - No incorpora autenticación completa, acceso por LAN ni una tecnología de persistencia concreta. La persistencia necesaria para inventario, IPAM o historial debe diseñarse antes de implementar esas herramientas; las decisiones de seguridad, privilegios y efectos sobre el sistema operativo se definirán por herramienta.
  - La pertenencia al MVP, el estado de implementación/despliegue y el estado de documentación son estados distintos y deben registrarse por separado.

### DEC-012

- **Estado**: APROBADA
- **Contexto**: Los contratos de API del Módulo 1 describen de manera desigual los errores HTTP y el formato común de error. La lógica de dominio debe conservarse independiente del transporte HTTP.
- **Decisión**: Los contratos de API del Módulo 1 compartirán un sobre JSON de error `{ "error": "<código>", "detail": "<mensaje>" }`. Los errores de validación de entrada y dominio usarán HTTP 422; los errores de sintaxis JSON conservarán la semántica aprobada en DEC-007; los tipos de contenido no admitidos usarán HTTP 415; las excepciones inesperadas usarán HTTP 500 con detalle seguro. Los contratos específicos conservarán los campos, rutas y códigos de error propios de cada herramienta.
- **Motivo**: Unificar la documentación pública del API y mantener una traducción coherente entre transporte y dominio, sin introducir dependencias HTTP en la lógica de negocio.
- **Consecuencias**:
  - `docs/modulo1/api-contracts.md` es la fuente común para el sobre de error y las reglas compartidas; cada contrato de herramienta define sus rutas, datos y códigos específicos.
  - Al aprobarse, las implementaciones de Subnetting, VLSM y Overlap aún tenían brechas frente al contrato. Estado revisado el 2026-10-18: las cuatro herramientas implementadas del Módulo 1 usan `422` para errores de validación y dominio, `415` para tipos de contenido no admitidos y mensajes de usuario en español.
  - DEC-007 sigue vigente para el tratamiento de errores de sintaxis JSON.

### DEC-013

- **Estado**: APROBADA
- **Contexto**: Los frontends de Overlap y VLSM insertaban mensajes de error y otros valores dinámicos mediante `innerHTML`. En Overlap, el detalle de error puede contener texto derivado de una red inválida suministrada por el usuario. Esto constituye un flujo estático de riesgo de inyección HTML; no se afirma que se haya demostrado explotación dinámica.
- **Decisión**: En Overlap y VLSM, construir los elementos dinámicos del DOM mediante APIs de nodos y presentar mensajes, valores de entrada y datos de respuesta con `textContent` o propiedades de formulario como `value`. No interpolar datos dinámicos en plantillas HTML interpretadas.
- **Motivo**: Evitar que datos de entrada, respuestas o errores se interpreten como marcado o código ejecutable, siguiendo el principio de presentación segura de datos no confiables.
- **Consecuencias**:
  - Se aplica a `src/netops_desk/static/js/overlap.js` y `src/netops_desk/static/js/vlsm.js`.
  - Se añaden guardas estáticas en `tests/test_frontend_static.py` para evitar la regresión de los sinks de renderizado identificados.
  - No se cambian contratos, rutas ni mensajes de dominio.
  - Las pruebas agregadas requieren ejecución autorizada; esta decisión no registra un resultado de pruebas.
- **Verificación**: La revisión estática identifica el flujo de datos; no se ejecutó una prueba de explotación ni una prueba de navegador como condición para aprobar este cambio.

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

- Excluir **ip** + **prefix** y compatibilidad retroactiva del contrato inicial.
- Permitir **mode** directo opcional, default **conventional**.
- Vocabulario público: **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**, **total_addresses**, **usable_addresses**, **binary**, **warnings**.
- Excluir temporalmente **classification** de la respuesta pública inicial y conservarla como funcionalidad aplazada.

## Decisiones formalizadas en esta actualización

- Respuesta inversa: **required_hosts**, **mode_requested**, **mode_applied**, **prefix**, **total_addresses**, **usable_addresses**, **warnings**; no incluye una red.
- **mode_requested** refleja la entrada. **mode_applied** es point-to-point solo si el prefijo elegido es /31 o /32 bajo ese modo; de otro modo es conventional.
- Evaluar prefijos /32 a /0 y elegir el primero con capacidad efectiva suficiente. La capacidad máxima es 4.294.967.294 en /0; excederla produce 422 **insufficient_capacity**.
- El objeto **binary** directo tiene exactamente seis claves: **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**. Valores en cuatro octetos de ocho bits separados por puntos; `null` se conserva.
- Cuerpo de error uniforme **{"error": "<code>", "detail": "<message>"}** y orden de validación como define el contrato.
- Se mantiene HTTP 400 `invalid_json` para errores de lectura/decodificación del cuerpo (ver DEC-007). Se mantiene HTTP 422 `invalid_json` para errores de sintaxis JSON.

## Bloqueados y aplazados

**classification** no forma parte del response público inicial. La función queda deseada y aplazada hasta verificar el catálogo exacto de asignaciones IANA y el vocabulario de salida.

---

*Este registro es parte de la documentación obligatoria y debe mantenerse actualizado a lo largo del proyecto. Solo las decisiones marcadas como `APROBADA` deben considerarse vinculantes para el alcance y la arquitectura del MVP.*
