# Estrategia de pruebas — Calculadora MTU y fragmentación

> Cobertura prevista para una herramienta pendiente de implementación. No se afirma que existan o se hayan ejecutado pruebas.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_mtu_calculator_domain.py` | Fórmulas puras, opciones, límites, advertencias y casos borde | Pendiente |
| API | `tests/test_api_mtu_calculator.py` | Request/response, defaults, validación y contrato HTTP | Pendiente |
| Interfaz/integración | Pruebas frontend por definir | Envío del formulario y presentación de resultados/advertencias | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| MTU default | Omitir `mtu` | El cálculo usa `1500` | Dominio/API | Pendiente; no ejecutado |
| MTU mínimo/máximo | `576`, `9000` | Aceptados | Dominio/API | Pendiente; no ejecutado |
| MTU fuera de rango | `575`, `9001` | Rechazo de validación | Dominio/API | Pendiente; no ejecutado |
| IPv4 TCP sin túnel | MTU 1500 | Con cabeceras fijas, `20 + 20`, resultado TCP 1460 | Dominio/API | Pendiente; no ejecutado |
| IPv6 | `ip_version="ipv6"` | Tamaño IP acorde con la regla que se apruebe | Dominio | Pendiente; regla exacta por formalizar |
| UDP | `transport="udp"` | Verificar el tamaño de datos UDP; resolver antes qué significa el campo `mss` | Dominio/API | Bloqueado por decisión pendiente |
| Valores enumerados inválidos | IP/transporte/túnel fuera de lista | Rechazo de validación | Dominio/API | Pendiente; no ejecutado |
| GRE/IPsec/WireGuard | Cada túnel seleccionado | Overhead exacto según perfil aprobado | Dominio/API | Bloqueado: perfiles no definidos |
| Advertencia por bajo MTU | Valor menor a 576 | Resolver si se rechaza o se devuelve advertencia | Dominio/API | Contradicción de requisitos pendiente |
| Resultado negativo | Overhead acumulado mayor al MTU | Advertencia y representación conforme a decisión pendiente | Dominio/API | Bloqueado por decisión pendiente |
| Semáforo agotado | Seis solicitudes concurrentes | Resultado según política de saturación que se apruebe | API | Pendiente; política no definida |

Para el caso IPv4/TCP se usa la definición de RFC 6691: el cálculo del MSS considera las cabeceras IP y TCP fijas; para 1500 bytes, 1500 − 20 − 20 = 1460. UDP tiene cabecera de 8 bytes según RFC 768, pero no debe etiquetarse automáticamente su carga como MSS TCP. Estos estándares sirven como fuentes independientes para los casos esperados.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea solo crea documentación.
- **Entorno:** No aplica a la auditoría documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar dominio/API/frontend y cerrar MTU-DEC-PEND-01 a 04 antes de probar resultados dependientes de decisiones aún abiertas.
