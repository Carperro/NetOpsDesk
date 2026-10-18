# Estrategia de pruebas — Planificador VLSM

## Alcance y capas

Esta estrategia registra la cobertura existente en la suite y las comprobaciones estáticas del frontend. No implica que los contratos pendientes de definición estén aprobados.

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_vlsm.py` | Validación de requerimientos, asignación descendente, capacidad, espacio restante, normalización, IPv4 y no solapamiento | Implementado |
| API | `tests/test_api_vlsm.py` | Respuesta exitosa, forma de la respuesta, validación Pydantic, errores y tipo de contenido | Implementado |
| Interfaz estática | `tests/test_frontend_static.py` | Página y recursos, campos principales, seguridad de inserción de datos dinámicos y formateador común de errores | Implementado mediante aserciones estáticas |
| Navegador | Suite de navegador/procedimiento manual | Interacción real, accesibilidad, presentación y flujo completo con navegador | No documentado como automatizado; requiere verificación visual cuando corresponda |

## Matriz de casos implementados

| Caso | Entrada representativa | Resultado esperado | Prueba | Estado de ejecución |
|---|---|---|---|---|
| Asignación normal | Tres requerimientos en una `/24` | Bloques ordenados de mayor a menor y espacio restante correcto | `test_vlsm_happy_path` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Ordenamiento independiente del orden ingresado | Lista pequeña, grande y mediana | Asignaciones ordenadas por `hosts` descendente | `test_vlsm_ordenamiento_automatico` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Requerimiento mayor que la red base | 500 hosts sobre `/24` | Error de dominio por bloque demasiado grande | `test_vlsm_red_muy_chica` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Requerimientos que exceden el espacio conjunto | Dos bloques `/25` y un `/30` en `/24` | Error de dominio por falta de espacio | `test_vlsm_sin_espacio` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Lista vacía en dominio | `requirements=[]` | Error de dominio | `test_vlsm_lista_vacia` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Límite exacto de capacidad | 254 hosts en `/24` | Una asignación `/24`, sin espacio restante | `test_vlsm_limite_exacto` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Enlace con dos hosts | 2 hosts en `/30` | Asignación `/30` completa | `test_vlsm_red_slash_30` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Consumo exacto | Dos requerimientos de 126 hosts en `/24` | Dos asignaciones `/25`, sin espacio restante | `test_vlsm_espacio_exacto` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Nombres repetidos | Dos requerimientos con el mismo nombre | Ambos se conservan; no se impone unicidad | `test_vlsm_nombres_duplicados` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Familia no admitida | Base IPv6 | Error explícito: VLSM solo soporta IPv4 | `test_vlsm_ipv6_rechazado` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Normalización sin mutar requerimientos | CIDR con bits de host y lista de entrada | Base normalizada y lista original intacta | `test_vlsm_normaliza_la_red_base_y_conserva_los_requerimientos` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Invariantes de asignación | Cuatro requerimientos en `/22` | Bloques ordenados, dentro de la base y sin solapamientos | `test_vlsm_asignaciones_no_se_solapan_y_quedan_dentro_de_la_red_base` | Suite ejecutada: pasó en la última verificación indicada abajo |
| CIDR inválido | Cadena que no es CIDR | Error de dominio | `test_vlsm_rechaza_cidr_malformado` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Rango restante | Asignación `/30` dentro de `/29` | Intervalo restante contiguo y cantidad inclusiva correcta | `test_vlsm_el_espacio_restante_es_contiguo_y_su_cantidad_inclusiva` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Nombre con contenido tipo HTML | Cadena `<img ...>` como nombre | El dominio conserva el dato como texto | `test_vlsm_nombres_con_caracteres_especiales_se_conservan_como_datos` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Esquema de API | Solicitud válida | HTTP `200` y claves exactas de salida | `test_api_vlsm_happy_path`, `test_api_vlsm_respuesta_contiene_el_esquema_completo` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Solicitud incompleta o mal tipada | Campos ausentes, lista vacía, host ausente o no entero | HTTP `422` y sobre `{error, detail}` | `test_api_vlsm_rechaza_solicitudes_incompletas_o_mal_tipadas` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Error de dominio y validación de campos | Capacidad insuficiente, host cero o nombre vacío | HTTP `422`, no `500` | `test_api_vlsm_error_dominio`, `test_api_vlsm_validacion_pydantic`, `test_api_vlsm_nombre_vacio` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Tipo de contenido no admitido | `Content-Type: text/plain` | HTTP `415` con sobre común | `test_api_vlsm_rechaza_tipo_de_contenido_no_admitido` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Página y recursos de frontend | `/tools/vlsm` y su JavaScript | Página servida, recursos y contenedores presentes | `test_vlsm_page_loads_its_script_and_result_containers` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Inserción segura y errores visibles | Datos dinámicos y mensaje de error | La suite estática impide interpolar datos en los destinos HTML señalados y comprueba escritura como texto | `test_vlsm_dynamic_values_are_not_interpolated_into_html` | Suite ejecutada: pasó en la última verificación indicada abajo |

## Límites de la cobertura actual

- Las pruebas estáticas no ejecutan JavaScript en un navegador ni demuestran por sí solas la seguridad de todos los flujos de renderizado.
- No hay un límite contractual de tamaño para la lista de requerimientos; no debe inferirse que listas ilimitadas estén aceptadas.
- Los nombres duplicados se aceptan actualmente. La prueba describe ese comportamiento observado, no una decisión de producto sobre unicidad.
- La prueba IPv6 confirma rechazo en el dominio; no prueba compatibilidad IPv6 de VLSM, que no forma parte del alcance funcional documentado actual.
- Los casos de subredes mínimas y rangos de hosts `/31`/`/32` no establecen semántica especial de asignación VLSM.
- Las pruebas de API comprueban el sobre de varios errores, pero la suite mostrada no cubre explícitamente JSON malformado, `405`, `500` inesperado ni solicitudes enormes.

## Ejecución y última verificación

- **Comando:** `.\.venv\Scripts\python.exe -m pytest tests/ -q`
- **Entorno:** Python 3.12, entorno virtual local del proyecto.
- **Fecha:** 2026-10-18.
- **Resultado observado:** 170 pruebas recolectadas y aprobadas, 0 fallidas, 0 omitidas (`170 passed in 1.05s`). La suite completa incluye los casos de dominio, API y guardas estáticas enumerados arriba.
- **Pendientes:** decidir límites de recursos y cualquier semántica especial de prefijos antes de convertir esos casos en requisitos; añadir automatización de navegador solo si el proyecto adopta y autoriza esa capa.
