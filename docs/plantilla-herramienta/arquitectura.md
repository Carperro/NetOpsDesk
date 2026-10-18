# Arquitectura — [Nombre de la herramienta]

> Describir la arquitectura implementada y aprobada. Distinguirla de alternativas propuestas.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | [módulo Python] | [reglas y cálculo] | [biblioteca estándar/dependencias aprobadas] |
| API | [modelos y rutas] | [validación de transporte y adaptación] | [dominio, FastAPI/Pydantic] |
| Interfaz | [HTML/CSS/JS] | [entrada, presentación y llamadas] | [API y recursos locales] |
| Pruebas | [archivos] | [comportamientos verificados] | [herramientas de pruebas] |

## Flujo principal

1. [Cómo se recibe y valida la entrada.]
2. [Cómo se invoca el caso de uso o dominio.]
3. [Cómo se forma la respuesta y se muestra en la interfaz.]

## Límites y errores

- **Validación en interfaz:** [solo experiencia de usuario; indicar reglas duplicadas por conveniencia].
- **Validación API/dominio:** [garantías e invariantes].
- **Errores y advertencias:** [referencia al contrato común y tratamiento específico].
- **Recursos y seguridad:** [límites, datos no confiables, dependencias externas o comandos si aplica].

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** [IDs y motivo; enlazar el decision-log].
- **Alternativas descartadas:** [solo si hay evidencia de evaluación].
- **Dependencias de plataforma/conectividad:** [o «Ninguna»].
- **Límites que permiten evolución futura:** [solo los existentes y justificados].
