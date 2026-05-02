from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import usuarios, laboratorios, servicios, tickets, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mesa de Servicios — Laboratorios Universitarios",
    description=(
        "API para gestión de tickets de servicios en laboratorios universitarios. "
        "Implementa autenticación JWT con scopes para control de acceso por rol."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router,          prefix="/auth",          tags=["Autenticación"])
app.include_router(usuarios.router,      prefix="/usuarios",      tags=["Usuarios"])
app.include_router(laboratorios.router,  prefix="/laboratorios",  tags=["Laboratorios"])
app.include_router(servicios.router,     prefix="/servicios",     tags=["Servicios"])
app.include_router(tickets.router,       prefix="/tickets",       tags=["Tickets"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "API de Mesa de Servicios en línea"}