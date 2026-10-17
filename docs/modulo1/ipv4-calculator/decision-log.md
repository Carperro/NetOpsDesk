# Registro de decisiones - NetOps Desk MVP

Este documento registra las decisiones aprobadas relevantes para el MVP de NetOps Desk. Cada decisión incluye un identificador estable, su estado, el contexto en que se tomó, la decisión misma, el motivo y las consecuencias. Las alternativas consideradas se registran solo cuando hay evidencia de que fueron evaluadas explícitamente.

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
