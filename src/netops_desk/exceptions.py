# src/netops_desk/exceptions.py

class DomainError(ValueError):
    """
    Excepción base para errores de reglas de negocio (dominio).
    
    Hereda de ValueError para mantener compatibilidad con los bloques 
    'except ValueError' existentes y con la librería estándar 'ipaddress'.
    """
    def __init__(self, message: str, code: str = "invalid_value"):
        super().__init__(message)
        self.message = message
        self.code = code