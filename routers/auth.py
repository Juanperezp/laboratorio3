from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from auth import verificar_password, crear_token, SCOPES_POR_ROL
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/token", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == form_data.username
    ).first()

    if not usuario or not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    scopes = SCOPES_POR_ROL.get(usuario.rol, [])

    token = crear_token({
        "sub": usuario.correo,
        "id_usuario": usuario.id_usuario,
        "rol": usuario.rol,
        "scopes": scopes
    })

    return {"access_token": token, "token_type": "bearer"}


    
