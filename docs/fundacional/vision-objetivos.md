# Visión y objetivos de NetOps Desk

## Visión del proyecto

NetOps Desk es una aplicación web que reúne herramientas habituales de redes y soporte técnico en una interfaz centralizada, organizada y fácil de utilizar.

## Objetivos principales

1. Construir una herramienta práctica para tareas de diagnóstico, cálculo y documentación de redes.
2. Desarrollar un proyecto de portfolio que demuestre conocimientos de Python, desarrollo web, redes, arquitectura de software, pruebas y buenas prácticas.

## Estado actual

MVP implementado: Calculadora IPv4/CIDR y Subnetting IPv4 accesibles desde el navegador mediante API FastAPI. Las demás herramientas del catálogo permanecen previstas.

El alcance detallado del MVP está en `docs/modulo1/ipv4-calculator/requisitos.md`. El catálogo completo con el estado de cada herramienta está en `docs/fundacional/catalogo.md`.

## Plataforma inicial

La aplicación funciona en una computadora con Windows, mediante un servidor local y una interfaz accesible desde el navegador.

## Requisitos arquitectónicos clave

- La arquitectura permite incorporar nuevas herramientas sin reescribir los componentes existentes.
- El dominio de cálculo es independiente de FastAPI, del navegador y de cualquier base de datos.
- La interfaz se carga sin dependencias externas obligatorias (sin CDN).
- Los cálculos de red tienen lógica verificable y pruebas de casos normales, límites y entradas inválidas.

Los principios completos están en `docs/fundacional/principios-estandar.md`.

## Criterio general de finalización

NetOps Desk se considera una base funcional sólida cuando dispone de:

- Una arquitectura comprensible y documentada.
- Al menos una herramienta verificada de punta a punta.
- Una API probada con contrato estable.
- Una interfaz local independiente de CDNs.
- Validación de entradas implementada en los límites del sistema.
- Documentación suficiente para continuar el desarrollo sin depender de decisiones implícitas.
