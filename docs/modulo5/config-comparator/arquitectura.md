# Arquitectura — Comparador de configuraciones

> Estado: arquitectura objetivo para la herramienta 23. El catálogo la marca pendiente de desarrollo e integración; las ubicaciones descritas son destino, no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/config_comparator.py` | Validar que haya contenido en al menos una entrada, generar el diff y calcular `has_changes` | Biblioteca estándar, en particular `difflib`; sin FastAPI, base de datos, sistema operativo ni red |
| API | Modelos y ruta por definir al implementar | Validar la solicitud, invocar el dominio y serializar `diff_lines` y `has_changes` | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por definir | Capturar ambas configuraciones y mostrar las diferencias | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar comparación pura, entradas límite y contrato HTTP | Pytest y cliente de API |

## Flujo principal

1. La interfaz envía `POST /api/v1/tools/config-comparator/compare` con `config_a` y `config_b`.
2. El modelo Pydantic valida que ambos campos sean strings y limita cada uno a 50.000 caracteres; la API tramita la operación bajo `asyncio.Semaphore(5)`.
3. El dominio rechaza la entrada si ambos textos están vacíos mediante `DomainError` con código `empty_configs`; el handler global lo traduce a HTTP 422.
4. El dominio usa `difflib.unified_diff` con `fromfile="Config A"`, `tofile="Config B"` y `lineterm=""` para formar `diff_lines`, y determina `has_changes`.
5. La API devuelve ambos resultados como JSON.
6. La interfaz muestra las diferencias como texto, sin interpretarlas como HTML.

Si el semáforo no tiene permisos disponibles, la API rechaza la solicitud con HTTP 429 y código `too_many_requests`.

## Semántica de comparación

- `config_a` representa el texto original y `config_b` el texto nuevo.
- `diff_lines` conserva el orden que produce el diff unificado entre el texto original y el nuevo.
- `has_changes` indica si los textos difieren. Si son iguales, el indicador es `false` y el diff no contiene diferencias.
- La comparación no interpreta comandos ni sintaxis de configuración; señala diferencias textuales.
- La entrada compuesta solo por espacios no está definida como vacía o con contenido y requiere una decisión antes de implementar.
- La llamada a `difflib.unified_diff` usa `fromfile="Config A"`, `tofile="Config B"` y `lineterm=""`. Los elementos de `diff_lines` corresponden a las líneas generadas sin saltos de línea finales agregados por el generador.

## Límites y errores

- **Validación en interfaz:** puede advertir si ambas cajas están vacías, pero la validación de la API y el dominio es obligatoria.
- **Validación API/dominio:** Pydantic limita cada entrada a 50.000 caracteres; el dominio rechaza ambas vacías con `DomainError(empty_configs)`.
- **Errores y advertencias:** `empty_configs` se traduce a HTTP 422 mediante el handler global. La saturación del semáforo responde HTTP 429 con `too_many_requests`. La respuesta de validación Pydantic por longitud sigue el manejo común de validación del Módulo 5.
- **Recursos y seguridad:** no leer ni escribir archivos a partir de las entradas. Los textos y el resultado del diff son datos no confiables y deben presentarse como texto. El límite de 50.000 caracteres por campo acota el tamaño del request; los límites de transporte adicionales corresponden a la configuración común de API.

## Concurrencia y evolución

La API usa `asyncio.Semaphore(5)` y rechaza con HTTP 429 `too_many_requests` cuando no hay permisos disponibles. El semáforo limita por proceso/event loop; su alcance global entre procesos workers no está definido por el alcance actual.

El dominio no necesita runner ni capa de persistencia: la comparación es una transformación local de dos strings. Mantener esta lógica independiente del transporte permite reutilizarla desde otra interfaz.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** comparación textual pura con `difflib.unified_diff` y parámetros fijados en este documento; entradas de hasta 50.000 caracteres cada una; `DomainError(empty_configs)` como HTTP 422; semáforo API de cinco permisos con HTTP 429 `too_many_requests` al agotarse (CFG-DEC-01 a CFG-DEC-03).
- **Alternativas descartadas:** no se requieren base de datos, operaciones del sistema operativo ni conectividad externa para comparar los textos.
- **Dependencias de plataforma/conectividad:** ninguna.
- **Límites que permiten evolución futura:** el algoritmo permanece en el dominio y la API se limita a adaptar el contrato HTTP.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 23](../../fundacional/catalogo.md).
