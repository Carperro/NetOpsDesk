# Checklist de revisión de cambios

Usá esta lista antes de solicitar revisión o integrar cambios. Es una guía de verificación: no aprueba decisiones ni amplía el alcance autorizado.

## Alcance y decisiones

- [ ] El cambio responde al pedido aprobado y afecta solo los archivos necesarios.
- [ ] Se consultaron `AGENTS.md`, `SKILLS.md` y las fuentes canónicas del módulo/herramienta.
- [ ] Las decisiones se distinguen de propuestas e inferencias; no se incorporaron decisiones nuevas sin aprobación.
- [ ] No se modificó código, configuración o documentación fuera del alcance autorizado.

## Contratos y comportamiento

- [ ] Entradas, salidas, validaciones y límites coinciden con el contrato vigente.
- [ ] Los errores conservan el sobre y la semántica HTTP comunes aplicables; los mensajes de interfaz son pertinentes y en español.
- [ ] Dominio, API, integración y presentación mantienen sus responsabilidades separadas.
- [ ] Se revisaron entradas inválidas, casos límite, normalización y errores pertinentes al cambio.

## Seguridad y robustez

- [ ] Datos no confiables se presentan como texto y no se interpretan como HTML o código.
- [ ] No se incorporaron secretos ni información sensible.
- [ ] Se consideraron límites de tamaño, tiempo y memoria para las entradas y colecciones afectadas.
- [ ] Las integraciones con sistema operativo validan argumentos y no introducen efectos externos no aprobados.

## Pruebas y calidad

- [ ] Se ejecutó `.\.venv\Scripts\python.exe -m pytest tests/ -q`; se informa el resultado real.
- [ ] Se ejecutó `pre-commit run --all-files` cuando corresponda.
- [ ] Los casos nuevos o modificados corresponden a requisitos o comportamientos definidos.
- [ ] No se afirma que se probó un navegador, plataforma o condición que no se verificó.

El hook actual ejecuta Ruff con las reglas críticas `E9,F63,F7,F82` y la suite completa de Pytest. El lint completo del repositorio sigue pendiente de una tarea separada; pasar el hook no equivale a aprobar todas las reglas configuradas en `pyproject.toml`.

## Documentación y entrega

- [ ] Se actualizaron las fuentes canónicas afectadas y se evitaron copias contradictorias.
- [ ] Las referencias a archivos existen y los ejemplos coinciden con el estado actual.
- [ ] El diff se revisó, no contiene cambios ajenos y pasa `git diff --check`.
- [ ] El trabajo se mantiene en `develop`; no se publica ni se integra a `main` sin autorización.
- [ ] El informe final enumera cambios, verificaciones, limitaciones y decisiones pendientes.
