from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from database import get_db
from models import Servicio, Usuario
from schemas import ServicioCreate, ServicioOut, ServicioUpdate
from auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ServicioOut, status_code=status.HTTP_201_CREATED)
def crear_servicio(
    datos: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    existente = db.query(Servicio).filter(Servicio.nombre == datos.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un servicio con ese nombre.")

    nuevo = Servicio(nombre=datos.nombre, descripcion=datos.descripcion, activo=datos.activo)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/", response_model=list[ServicioOut])
def listar_servicios(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=[]),
):
    query = db.query(Servicio)
    if solo_activos:
        query = query.filter(Servicio.activo == True)
    return query.all()


@router.get("/{id_servicio}", response_model=ServicioOut)
def obtener_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=[]),
):
   
    servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")
    return servicio


@router.patch("/{id_servicio}", response_model=ServicioOut)
def actualizar_servicio(
    id_servicio: int,
    datos: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
   
    servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")

    if datos.nombre is not None:
        duplicado = db.query(Servicio).filter(
            Servicio.nombre == datos.nombre,
            Servicio.id_servicio != id_servicio
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otro servicio con ese nombre.")
        servicio.nombre = datos.nombre
    if datos.descripcion is not None:
        servicio.descripcion = datos.descripcion
    if datos.activo is not None:
        servicio.activo = datos.activo

    db.commit()
    db.refresh(servicio)
    return servicio


@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")
    servicio.activo = False
    db.commit()
