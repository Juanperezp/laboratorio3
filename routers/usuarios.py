from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioOut, UsuarioUpdate
from auth import get_current_user
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    #current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    existente = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo.")

    nuevo = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=pwd_context.hash(datos.password),
        rol=datos.rol,
        activo=datos.activo,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro_publico(datos: UsuarioCreate, db: Session = Depends(get_db)):
    
    if datos.rol != "solicitante":
        raise HTTPException(status_code=403, detail="El registro público solo permite el rol 'solicitante'.")

    existente = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo.")

    nuevo = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=pwd_context.hash(datos.password),
        rol=datos.rol,
        activo=datos.activo,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    return db.query(Usuario).all()


@router.get("/me", response_model=UsuarioOut)
def obtener_perfil(current_user: Usuario = Security(get_current_user, scopes=[])):
    
    return current_user


@router.get("/{id_usuario}", response_model=UsuarioOut)
def obtener_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario


@router.patch("/{id_usuario}", response_model=UsuarioOut)
def actualizar_usuario(
    id_usuario: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.correo is not None:
        duplicado = db.query(Usuario).filter(
            Usuario.correo == datos.correo, Usuario.id_usuario != id_usuario
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="El correo ya está en uso.")
        usuario.correo = datos.correo
    if datos.rol is not None:
        usuario.rol = datos.rol
    if datos.activo is not None:
        usuario.activo = datos.activo
    if datos.password is not None:
        usuario.password_hash = pwd_context.hash(datos.password)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id_usuario == current_user.id_usuario:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo.")
    usuario.activo = False
    db.commit()