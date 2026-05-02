from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from database import get_db
from models import Laboratorio, Usuario
from schemas import LaboratorioCreate, LaboratorioOut, LaboratorioUpdate
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=LaboratorioOut, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(
    datos: LaboratorioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    existente = db.query(Laboratorio).filter(Laboratorio.nombre == datos.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un laboratorio con ese nombre.")

    nuevo = Laboratorio(nombre=datos.nombre, ubicacion=datos.ubicacion, activo=datos.activo)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/", response_model=list[LaboratorioOut])
def listar_laboratorios(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=[]),
):
    
    query = db.query(Laboratorio)
    if solo_activos:
        query = query.filter(Laboratorio.activo == True)
    return query.all()


@router.get("/{id_laboratorio}", response_model=LaboratorioOut)
def obtener_laboratorio(
    id_laboratorio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=[]),
):

    lab = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado.")
    return lab


@router.patch("/{id_laboratorio}", response_model=LaboratorioOut)
def actualizar_laboratorio(
    id_laboratorio: int,
    datos: LaboratorioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    lab = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado.")

    if datos.nombre is not None:
        duplicado = db.query(Laboratorio).filter(
            Laboratorio.nombre == datos.nombre,
            Laboratorio.id_laboratorio != id_laboratorio
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otro laboratorio con ese nombre.")
        lab.nombre = datos.nombre
    if datos.ubicacion is not None:
        lab.ubicacion = datos.ubicacion
    if datos.activo is not None:
        lab.activo = datos.activo

    db.commit()
    db.refresh(lab)
    return lab


@router.delete("/{id_laboratorio}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_laboratorio(
    id_laboratorio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Security(get_current_user, scopes=["usuarios:gestionar"]),
):
    
    lab = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado.")
    lab.activo = False
    db.commit()