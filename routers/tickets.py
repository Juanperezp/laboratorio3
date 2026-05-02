from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from database import get_db
from auth import get_usuario_actual
from datetime import datetime
import models
import schemas

router = APIRouter(prefix="/tickets", tags=["Tickets"])

TRANSICIONES_PERMITIDAS = {
    "solicitado": "recibido",
    "recibido": "asignado",
    "asignado": "en_proceso",
    "en_proceso": "en_revision",
    "en_revision": "terminado"
}

SCOPE_POR_TRANSICION = {
    "recibido": "tickets:recibir",
    "asignado": "tickets:asignar",
    "en_proceso": "tickets:atender",
    "en_revision": "tickets:atender",
    "terminado": "tickets:finalizar"
}

@router.post("/", response_model=schemas.TicketRespuesta)
def crear_ticket(
    ticket: schemas.TicketCrear,
    db: Session = Depends(get_db),
    usuario_actual=Security(get_usuario_actual, scopes=["tickets:crear"])
):
    nuevo = models.Ticket(
        id_solicitante=usuario_actual.id_usuario,
        id_laboratorio=ticket.id_laboratorio,
        id_servicio=ticket.id_servicio,
        titulo=ticket.titulo,
        descripcion=ticket.descripcion,
        prioridad=ticket.prioridad,
        estado="solicitado"
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[schemas.TicketRespuesta])
def listar_tickets(
    db: Session = Depends(get_db),
    usuario_actual=Security(get_usuario_actual, scopes=["tickets:ver_propios"])
):
    if "admin" == usuario_actual.rol:
        return db.query(models.Ticket).all()

    return db.query(models.Ticket).filter(
        (models.Ticket.id_solicitante == usuario_actual.id_usuario) |
        (models.Ticket.id_asignado == usuario_actual.id_usuario) |
        (models.Ticket.id_responsable == usuario_actual.id_usuario)
    ).all()

@router.get("/{id_ticket}", response_model=schemas.TicketRespuesta)
def obtener_ticket(
    id_ticket: int,
    db: Session = Depends(get_db),
    usuario_actual=Security(get_usuario_actual, scopes=["tickets:ver_propios"])
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id_ticket == id_ticket
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if usuario_actual.rol != "admin":
        if usuario_actual.id_usuario not in [
            ticket.id_solicitante,
            ticket.id_asignado,
            ticket.id_responsable
        ]:
            raise HTTPException(status_code=403, detail="No tienes acceso a este ticket")

    return ticket

@router.patch("/{id_ticket}/estado", response_model=schemas.TicketRespuesta)
def cambiar_estado(
    id_ticket: int,
    datos: schemas.TicketEstado,
    db: Session = Depends(get_db),
    usuario_actual=Security(get_usuario_actual, scopes=["tickets:ver_propios"])
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id_ticket == id_ticket
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    nuevo_estado = datos.estado
    estado_actual = ticket.estado

    if TRANSICIONES_PERMITIDAS.get(estado_actual) != nuevo_estado:
        raise HTTPException(
            status_code=422,
            detail=f"Transición no permitida: {estado_actual} → {nuevo_estado}"
        )

    scope_requerido = SCOPE_POR_TRANSICION.get(nuevo_estado)
    from jose import jwt
    from auth import SECRET_KEY, ALGORITHM
    from fastapi.security import SecurityScopes

    token_scopes_check = Security(get_usuario_actual, scopes=[scope_requerido])

    if nuevo_estado in ["en_proceso", "en_revision"]:
        if usuario_actual.rol != "admin" and ticket.id_asignado != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="Solo el técnico asignado puede realizar esta acción"
            )

    if nuevo_estado == "asignado" and datos.id_asignado:
        ticket.id_asignado = datos.id_asignado
        ticket.id_responsable = usuario_actual.id_usuario

    if datos.observacion_responsable:
        ticket.observacion_responsable = datos.observacion_responsable
    if datos.observacion_tecnico:
        ticket.observacion_tecnico = datos.observacion_tecnico

    ticket.estado = nuevo_estado
    ticket.fecha_actualizacion = datetime.utcnow()

    if nuevo_estado == "terminado":
        ticket.fecha_finalizacion = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket
