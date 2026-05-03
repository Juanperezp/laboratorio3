from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


ROLES_VALIDOS = {
    "solicitante",
    "responsable_tecnico",
    "auxiliar",
    "tecnico_especializado",
    "admin",
}


class UsuarioBase(BaseModel):
    nombre: str
    correo: str
    rol: str
    activo: bool = True

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: str) -> str:
        if v not in ROLES_VALIDOS:
            raise ValueError(
                f"Rol inválido. Debe ser uno de: {', '.join(ROLES_VALIDOS)}"
            )
        return v


class UsuarioCreate(UsuarioBase):
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return v


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ROLES_VALIDOS:
            raise ValueError(
                f"Rol inválido. Debe ser uno de: {', '.join(ROLES_VALIDOS)}"
            )
        return v


class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    rol: str
    activo: bool

    model_config = {"from_attributes": True}

class LaboratorioBase(BaseModel):
    nombre: str
    ubicacion: str
    activo: bool = True


class LaboratorioCreate(LaboratorioBase):
    pass


class LaboratorioUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    activo: Optional[bool] = None


class LaboratorioOut(LaboratorioBase):
    id_laboratorio: int

    model_config = {"from_attributes": True}


class ServicioBase(BaseModel):
    nombre: str
    descripcion: str
    activo: bool = True


class ServicioCreate(ServicioBase):
    pass


class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class ServicioOut(ServicioBase):
    id_servicio: int

    model_config = {"from_attributes": True}


ESTADOS_VALIDOS = {
    "solicitado",
    "recibido",
    "asignado",
    "en_proceso",
    "en_revision",
    "terminado",
}

PRIORIDADES_VALIDAS = {"baja", "media", "alta"}


class TicketBase(BaseModel):
    titulo: str
    descripcion: str
    prioridad: str = "media"
    id_laboratorio: int
    id_servicio: int

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: str) -> str:
        if v not in PRIORIDADES_VALIDAS:
            raise ValueError(
                f"Prioridad inválida. Debe ser: {', '.join(PRIORIDADES_VALIDAS)}"
            )
        return v


class TicketCreate(TicketBase):
    pass


class TicketEstadoUpdate(BaseModel):
    estado: str
    observacion_responsable: Optional[str] = None
    observacion_tecnico: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str) -> str:
        if v not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS_VALIDOS)}"
            )
        return v


class TicketAsignar(BaseModel):
    id_asignado: int
    observacion_responsable: Optional[str] = None


class TicketOut(TicketBase):
    id_ticket: int
    id_solicitante: int
    id_responsable: Optional[int] = None
    id_asignado: Optional[int] = None
    estado: str
    observacion_responsable: Optional[str] = None
    observacion_tecnico: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_finalizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    correo: Optional[str] = None
    id_usuario: Optional[int] = None
    rol: Optional[str] = None
    scopes: list[str] = []
    
    
TicketRespuesta = TicketOut
TicketCrear = TicketCreate
TicketEstado = TicketEstadoUpdate
LaboratorioCrear = LaboratorioCreate
LaboratorioRespuesta = LaboratorioOut
ServicioCrear = ServicioCreate
ServicioRespuesta = ServicioOut
Token = Token
