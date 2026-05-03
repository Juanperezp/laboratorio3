from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import get_db
import models
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SCOPES_POR_ROL = {
    "solicitante": ["tickets:crear", "tickets:ver_propios"],
    "responsable_tecnico": ["tickets:ver_propios", "tickets:recibir", "tickets:asignar", "tickets:finalizar"],
    "auxiliar": ["tickets:ver_propios", "tickets:atender"],
    "tecnico_especializado": ["tickets:ver_propios", "tickets:atender"],
    "admin": [
        "tickets:crear", "tickets:ver_propios", "tickets:recibir",
        "tickets:asignar", "tickets:atender", "tickets:finalizar",
        "tickets:ver_todos", "usuarios:gestionar"
    ]
}

def verificar_password(password_plano, password_hash):
    return pwd_context.verify(password_plano, password_hash)

def hashear_password(password):
    return pwd_context.hash(password)

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_actual(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": authenticate_value}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credenciales_exception
        token_scopes = payload.get("scopes", [])
    except JWTError:
        raise credenciales_exception

    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if usuario is None:
        raise credenciales_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso. Se requiere el scope: {scope}"
            )

    return usuario

get_current_user = get_usuario_actual

