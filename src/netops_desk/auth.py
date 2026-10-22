"""Lógica de autenticación y manejo de tokens JWT."""

from datetime import datetime, timedelta, timezone
import os
import jwt
from netops_desk.repositories.user_repository import SQLiteUserRepository, password_hash
from netops_desk.exceptions import DomainError

# Clave de desarrollo local; los entornos de entrega deben definir NETOPS_SECRET_KEY.
SECRET_KEY = os.getenv("NETOPS_SECRET_KEY", "netops-desk-super-secret-key-local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

def authenticate_user(repo: SQLiteUserRepository, username: str, password: str) -> str:
    user = repo.get_by_username(username)
    # Cambiamos pwd_context.verify por password_hash.verify
    if not user or not password_hash.verify(password, user["password_hash"]):
        raise DomainError(message="Credenciales inválidas.", code="invalid_credentials")
    
    # Crear el token JWT
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user["username"],
        "role": user["role"],
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise DomainError(message="El token ha expirado.", code="token_expired")
    except jwt.InvalidTokenError:
        raise DomainError(message="Token inválido.", code="invalid_token")
