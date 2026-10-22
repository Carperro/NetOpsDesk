# Arquitectura — Generador de comandos

> Arquitectura objetivo aprobada; no describe componentes implementados.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `netops_desk/command_generator.py` | Mantener los diccionarios estáticos de plantillas y la lógica condicional para validar el catálogo, armar el comando, explicar sus opciones y determinar `requires_admin` | Biblioteca estándar; sin FastAPI, navegador ni ejecución de procesos |
| API | Ruta y modelos aún por definir | Validar el request, adquirir el semáforo, invocar el dominio y adaptar el resultado o error a HTTP/JSON | FastAPI, Pydantic y dominio |
| Interfaz | HTML/CSS/JavaScript aún por definir | Ofrecer selector y campos dinámicos; mostrar el resultado como texto copiable | API y recursos locales |
| Pruebas | Archivos aún por definir | Verificar whitelist, armado, validación, respuestas HTTP y presentación segura | Herramientas de pruebas aprobadas |

## Flujo principal

1. La interfaz envía `command_type`, `target` y `options` a la operación de generación.
2. La API valida el esquema y trata de adquirir uno de los cinco permisos del semáforo. Si está agotado, responde HTTP 429 con `too_many_requests`.
3. El dominio valida el tipo y cada opción contra la whitelist estática. Para `ping`, `tracert` y `nslookup`, exige un objetivo válido; para `ipconfig` y `netstat`, permite omitirlo o enviarlo vacío.
4. El dominio arma `command` y `explanation`, y calcula `requires_admin` usando la matriz de privilegios aprobada. No invoca el sistema operativo.
5. La API devuelve `command`, `explanation` y `requires_admin` como JSON; la interfaz los presenta como texto.

## Límites y errores

- **Validación en interfaz:** adapta campos al tipo seleccionado y puede anticipar errores para mejorar la experiencia; no sustituye la validación del servidor.
- **Validación API/dominio:** el dominio acepta exclusivamente cinco tipos y las opciones enumeradas en la whitelist de [requisitos](requisitos.md). `ping`, `tracert` y `nslookup` requieren IP o dominio válido. `ipconfig` y `netstat` permiten `target` vacío u omitido.
- **Errores y advertencias:** errores de validación HTTP 422: `invalid_command_type`, `missing_target`, `invalid_target` e `invalid_option`. Semáforo agotado: HTTP 429 `too_many_requests`. El sobre JSON común del Módulo 5 debe seguir la política transversal que corresponda; no se infiere DEC-012, que rige el Módulo 1.
- **Recursos y seguridad:** el comando solo se devuelve como dato para copiar. No ejecutar `subprocess`, shell ni comandos por otro mecanismo. La whitelist evita incorporar opciones arbitrarias. Presentar comando, explicación y mensajes como texto, no como HTML interpretado.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dominio puro en `netops_desk/command_generator.py`, plantillas estáticas, construcción condicional, whitelist estricta y generación sin ejecución. Referencia: [registro de decisiones](decision-log.md).
- **Alternativas descartadas:** ejecutar el comando mediante `subprocess` queda fuera del alcance de esta herramienta.
- **Dependencias de plataforma/conectividad:** las plantillas son comandos de Windows; generar el texto no requiere conectividad ni ejecución local.
- **Límites que permiten evolución futura:** el dominio conserva el catálogo y la construcción separados de HTTP y la interfaz; cualquier ampliación de comandos u opciones requiere actualizar la whitelist y sus pruebas.