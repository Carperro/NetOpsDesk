# Arquitectura — Detector de solapamiento de redes

## Componentes

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Dominio | `src/netops_desk/overlap.py` | Parsear y normalizar redes IPv4, comparar pares y generar conflictos. No depende de FastAPI ni Pydantic. |
| Modelo API | `src/netops_desk/api/models/overlap.py` | Validar entrada `networks` y definir la respuesta y sus conflictos. Rechaza campos adicionales y exige al menos dos entradas. |
| Ruta API | `src/netops_desk/api/routes/overlap.py` | Exponer el endpoint, validar Content-Type mediante dependencia común, invocar dominio y serializar el resultado. |
| Interfaz | `src/netops_desk/static/tools/overlap.html`, `src/netops_desk/static/js/overlap.js` | Recibir redes por línea, llamar a la API y presentar estado y conflictos. |
| Pruebas | `tests/test_overlap.py`, `tests/test_api_overlap.py`, `tests/test_frontend_static.py` | Verificar dominio, contrato HTTP y estructura/presentación estática del frontend. |

No hay una capa de servicio específica: la ruta invoca directamente la función de dominio.

## Flujo principal

1. El frontend divide el texto por líneas, recorta espacios y descarta líneas vacías.
2. El navegador envía `POST /api/v1/tools/overlap/calculate` con JSON `{ "networks": [...] }`.
3. La API aplica el modelo Pydantic y exige `application/json`.
4. `detect_overlaps` convierte cada valor con `ipaddress.ip_network(..., strict=False)`, rechaza redes que no sean IPv4 y compara todas las combinaciones de pares.
5. La respuesta tipada contiene las cadenas originales, un booleano y la lista de conflictos.
6. La interfaz crea nodos y presenta valores dinámicos con `textContent`, conforme a DEC-013.

## Límites, errores y recursos

- La validación de longitud mínima está en el modelo de API y también en el dominio, que puede ser invocado fuera de HTTP.
- Los errores de dominio se traducen mediante el handler global a HTTP 422 con el sobre común `{ "error": "<código>", "detail": "<mensaje>" }`.
- Un Content-Type no admitido produce HTTP 415. Los errores de esquema y método usan los handlers comunes del proyecto.
- La comparación usa `itertools.combinations` y no tiene límite máximo de redes definido. Un límite de recursos queda pendiente de decisión.
- Las redes son datos de entrada no confiables. La interfaz usa `textContent` para mensajes y valores dinámicos; no interpola estos datos en HTML interpretado.

## Decisiones relacionadas

- **DEC-011:** Overlap pertenece al MVP.
- **DEC-012:** se aplica el contrato común de errores HTTP.
- **DEC-013:** los datos dinámicos se muestran mediante APIs seguras del DOM.
- No se encontró una decisión aprobada específica de Overlap sobre tamaño máximo de entrada.
