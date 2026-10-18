# Visión y objetivos de NetOps Desk

## Visión del proyecto

NetOps Desk es una aplicación web que reúne herramientas habituales de redes y soporte técnico en una interfaz centralizada, organizada y fácil de utilizar.

## Objetivos principales

1. Construir una herramienta práctica para tareas de diagnóstico, cálculo y documentación de redes.
2. Desarrollar un proyecto de portfolio que demuestre conocimientos de Python, desarrollo web, redes, arquitectura de software, pruebas y buenas prácticas.

## Estado actual

El MVP comprende las 25 herramientas del catálogo oficial. Su desarrollo e integración con el frontend avanzan progresivamente; el catálogo indica el estado de implementación, despliegue y documentación de cada herramienta.

El catálogo oficial y el estado de cada herramienta están en `docs/fundacional/catalogo.md`. Los requisitos específicos se mantienen en la carpeta de documentación de cada herramienta.

## Plataforma inicial

La aplicación funciona en una computadora con Windows, mediante un servidor local y una interfaz accesible desde el navegador.

## Requisitos arquitectónicos clave

- La arquitectura permite incorporar nuevas herramientas sin reescribir los componentes existentes.
- El dominio de cálculo es independiente de FastAPI, del navegador y de cualquier base de datos.
- La interfaz se carga sin dependencias externas obligatorias (sin CDN).
- Los cálculos de red tienen lógica verificable y pruebas de casos normales, límites y entradas inválidas.

Los principios completos están en `docs/fundacional/principios-estandar.md`.

## Criterios de finalización

El MVP se considera completo cuando las 25 herramientas del catálogo estén desarrolladas e integradas con el frontend, de acuerdo con DEC-011.

Mientras el MVP avanza, NetOps Desk cuenta con una base funcional sólida cuando dispone de:

- Una arquitectura comprensible y documentada.
- Al menos una herramienta verificada de punta a punta.
- Una API probada con contrato estable.
- Una interfaz local independiente de CDNs.
- Validación de entradas implementada en los límites del sistema.
- Documentación suficiente para continuar el desarrollo sin depender de decisiones implícitas.
