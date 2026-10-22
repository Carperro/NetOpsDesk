"""Lógica de dominio para el Asistente de Resolución de Problemas."""

from __future__ import annotations
from typing import TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "SymptomResult", "get_symptom"]

class ErrorCode:
    INVALID_SYMPTOM = "invalid_symptom"

class Cause(TypedDict):
    cause: str
    steps: list[str]

class SymptomResult(TypedDict):
    symptom_id: str
    symptom_name: str
    causes: list[Cause]

# Base de conocimiento estática
SYMPTOM_DATABASE: dict[str, SymptomResult] = {
    "sin_internet": {
        "symptom_id": "sin_internet",
        "symptom_name": "Sin acceso a internet",
        "causes": [
            {
                "cause": "Conexión local interrumpida",
                "steps": [
                    "Verificar que el cable de red esté conectado o que el Wi-Fi esté encendido.",
                    "Revisar si las luces del router/módem están encendidas.",
                    "Reiniciar el adaptador de red desde el Panel de Control."
                ]
            },
            {
                "cause": "Configuración IP o gateway incorrectos",
                "steps": [
                    "Abrir CMD y ejecutar 'ipconfig /all'.",
                    "Verificar que la IP, máscara y Gateway no sean 0.0.0.0 ni empiecen con 169.254.x.x.",
                    "Ejecutar 'ipconfig /release' y luego 'ipconfig /renew'."
                ]
            },
            {
                "cause": "Falla en el equipo de acceso o en el proveedor",
                "steps": [
                    "Hacer ping al Gateway (ej. 'ping 192.168.1.1').",
                    "Hacer ping a una IP pública (ej. 'ping 8.8.8.8').",
                    "Si el Gateway responde pero la IP pública no, contactar al proveedor de internet."
                ]
            }
        ]
    },
    "internet_lento": {
        "symptom_id": "internet_lento",
        "symptom_name": "Latencia alta o pérdida de paquetes",
        "causes": [
            {
                "cause": "Interferencia inalámbrica (Wi-Fi)",
                "steps": [
                    "Acercarse al router.",
                    "Cambiar el canal del Wi-Fi en la configuración del router.",
                    "Considerar el uso de un cable Ethernet para descartar problemas inalámbricos."
                ]
            },
            {
                "cause": "Ancho de banda saturado",
                "steps": [
                    "Verificar si hay descargas activas en la red.",
                    "Revisar el uso de ancho de banda en el Administrador de Tareas (Windows).",
                    "Priorizar el tráfico con QoS en el router si es posible."
                ]
            },
            {
                "cause": "Problemas con el DNS",
                "steps": [
                    "Probar cambiar los DNS a 8.8.8.8 (Google) o 1.1.1.1 (Cloudflare).",
                    "Ejecutar 'ipconfig /flushdns' para limpiar la caché."
                ]
            }
        ]
    },
    "dns_falla": {
        "symptom_id": "dns_falla",
        "symptom_name": "No resuelve nombres de dominio",
        "causes": [
            {
                "cause": "Servidor DNS no configurado o caído",
                "steps": [
                    "Verificar los servidores DNS en 'ipconfig /all'.",
                    "Hacer 'nslookup google.com' para ver qué responde.",
                    "Cambiar el DNS primario a 8.8.8.8."
                ]
            },
            {
                "cause": "Caché de DNS corrupta",
                "steps": [
                    "Abrir CMD como administrador.",
                    "Ejecutar 'ipconfig /flushdns'.",
                    "Reiniciar el navegador."
                ]
            },
            {
                "cause": "Archivo hosts modificado",
                "steps": [
                    "Ir a C:\\Windows\\System32\\drivers\\etc\\",
                    "Abrir el archivo 'hosts' con el Bloc de notas.",
                    "Verificar que no haya entradas maliciosas o incorrectas para el dominio que falla."
                ]
            }
        ]
    }
}

def get_symptom(*, symptom_id: str) -> SymptomResult:
    """Devuelve los datos del síntoma o lanza un error."""
    symptom = SYMPTOM_DATABASE.get(symptom_id)
    if not symptom:
        raise DomainError(
            message="El síntoma solicitado no existe en el catálogo.",
            code=ErrorCode.INVALID_SYMPTOM
        )
    return symptom