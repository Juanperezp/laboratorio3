from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

class Laboratorio(Base):
    __tablename__ = "laboratorios"

    id_laboratorio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ubicacion = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

class Servicio(Base):
    __tablename__ = "servicios"

    id_servicio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"

    id_ticket = Column(Integer, primary_key=True, index=True)
    id_solicitante = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_laboratorio = Column(Integer, ForeignKey("laboratorios.id_laboratorio"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicios.id_servicio"), nullable=False)
    id_responsable = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    id_asignado = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String, default="solicitado")
    prioridad = Column(String, nullable=False)
    observacion_responsable = Column(Text, nullable=True)
    observacion_tecnico = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_finalizacion = Column(DateTime, nullable=True)

    solicitante = relationship("Usuario", foreign_keys=[id_solicitante])
    responsable = relationship("Usuario", foreign_keys=[id_responsable])
    asignado = relationship("Usuario", foreign_keys=[id_asignado])
    laboratorio = relationship("Laboratorio")
    servicio = relationship("Servicio")