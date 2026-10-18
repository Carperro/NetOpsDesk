# Requisitos — Detector de solapamiento de redes

## Propósito y alcance

El Detector de solapamiento es la herramienta 4 del Módulo 1. Su objetivo es comparar redes IPv4 en notación CIDR, identificar pares que se solapan y explicar si una red contiene a la otra o si el solapamiento es parcial. Forma parte del MVP por DEC-011.

El catálogo describe su alcance como comparación de rangos CIDR y detección de conflictos. La implementación actual admite IPv4; no se debe inferir soporte IPv6.

## Comportamiento funcional observado

- Recibe al menos dos redes CIDR.
- Normaliza bits de host para comparar las redes, pero conserva las cadenas de entrada en `networks` de la respuesta.
- Devuelve todos los pares solapados en orden de entrada.
- Informa redes iguales o contenidas y solapamientos parciales.
- No considera solapadas dos redes adyacentes.
- Rechaza redes inválidas y redes IPv6 con errores de dominio.
- La interfaz admite una red por línea, elimina líneas vacías y espacios de borde, y realiza una comprobación local de mínimo dos redes antes de llamar a la API.

Estos puntos describen el comportamiento respaldado por el código y las pruebas actuales. Los límites máximos de entrada y requisitos adicionales de producto no están definidos en la documentación revisada.

## Criterios de aceptación implementados

| ID | Criterio | Evidencia de prueba |
|---|---|---|
| OVL-AC-01 | Dos o más redes independientes producen `has_overlap: false` y una lista `overlaps` vacía. | `tests/test_overlap.py`, `tests/test_api_overlap.py` |
| OVL-AC-02 | Redes parcialmente solapadas, iguales o contenidas aparecen como pares con explicación. | `tests/test_overlap.py`, `tests/test_api_overlap.py` |
| OVL-AC-03 | La comparación normaliza CIDR con bits de host y conserva la entrada original en la respuesta. | `tests/test_overlap.py`, `tests/test_api_overlap.py` |
| OVL-AC-04 | Una entrada con menos de dos redes, CIDR inválido o IPv6 se rechaza. | `tests/test_overlap.py`, `tests/test_api_overlap.py` |
| OVL-AC-05 | Los datos de error y conflicto se insertan como texto en la interfaz. | `tests/test_frontend_static.py` |

## Límites y cuestiones pendientes

- No hay un máximo documentado para la cantidad de redes. El dominio compara pares, por lo que el número de comparaciones crece cuadráticamente con la cantidad de entradas. Definir un límite es una decisión pendiente, no un requisito aprobado en este documento.
- **Discrepancia visual observada:** `src/netops_desk/static/tools/overlap.html` conserva `<title>` y `<h1>` con el texto “Planificador VLSM” aunque su formulario y operación son de solapamiento. Este hallazgo se documenta; no se corrige como parte de este commit documental.
