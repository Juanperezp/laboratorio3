# Laboratorio 3 — Mesa de Servicios para Laboratorios Universitarios

API REST para gestión de tickets de servicios, construida con FastAPI, PostgreSQL y autenticación JWT con scopes.

---

## Integrantes

| Nombre | Aporte |
|---|---|
| Juan Diego  Pérez | `database.py`, `models.py`, `auth.py`, `routers/tickets.py` |
| Valentina Zapata | `schemas.py`, `main.py`, `routers/usuarios.py`, `routers/laboratorios.py`, `routers/servicios.py` |

---

## Estructura del proyecto

```
laboratorio3/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── requirements.txt
├── .env               # No incluido en el repositorio
├── .gitignore
└── routers/
    ├── __init__.py
    ├── auth.py
    ├── usuarios.py
    ├── laboratorios.py
    ├── servicios.py
    └── tickets.py
```

---

## Configuración

**1. Clonar el repositorio y crear el entorno virtual**

```bash
git clone https://github.com/Juanperezp/laboratorio3.git
cd laboratorio3
python -m venv venv
source venv/bin/activate   
```

**2. Instalar dependencias**

```bash
pip install -r requirements.txt
```


**3. Ejecutar**

```bash
uvicorn main:app --reload
```

Swagger disponible en: http://localhost:8000/docs

---

## Endpoints

### Autenticación
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/auth/token` | Login. Retorna token JWT |

### Usuarios
| Método | Ruta | Scope requerido |
|---|---|---|
| `POST` | `/usuarios/registro` | Público (solo rol `solicitante`) |
| `POST` | `/usuarios/` | `usuarios:gestionar` |
| `GET` | `/usuarios/` | `usuarios:gestionar` |
| `GET` | `/usuarios/me` | Autenticado |
| `GET` | `/usuarios/{id}` | `usuarios:gestionar` |
| `PATCH` | `/usuarios/{id}` | `usuarios:gestionar` |
| `DELETE` | `/usuarios/{id}` | `usuarios:gestionar` |

### Laboratorios
| Método | Ruta | Scope requerido |
|---|---|---|
| `POST` | `/laboratorios/` | `usuarios:gestionar` |
| `GET` | `/laboratorios/` | Autenticado |
| `GET` | `/laboratorios/{id}` | Autenticado |
| `PATCH` | `/laboratorios/{id}` | `usuarios:gestionar` |
| `DELETE` | `/laboratorios/{id}` | `usuarios:gestionar` |

### Servicios
| Método | Ruta | Scope requerido |
|---|---|---|
| `POST` | `/servicios/` | `usuarios:gestionar` |
| `GET` | `/servicios/` | Autenticado |
| `GET` | `/servicios/{id}` | Autenticado |
| `PATCH` | `/servicios/{id}` | `usuarios:gestionar` |
| `DELETE` | `/servicios/{id}` | `usuarios:gestionar` |

### Tickets
| Método | Ruta | Scope requerido |
|---|---|---|
| `POST` | `/tickets/` | `tickets:crear` |
| `GET` | `/tickets/` | `tickets:ver_propios` |
| `GET` | `/tickets/{id}` | `tickets:ver_propios` |
| `PATCH` | `/tickets/{id}/estado` | Depende de la transición |

---

## Roles y scopes

| Rol | Scopes |
|---|---|
| `solicitante` | `tickets:crear`, `tickets:ver_propios` |
| `responsable_tecnico` | `tickets:ver_propios`, `tickets:recibir`, `tickets:asignar`, `tickets:finalizar` |
| `auxiliar` | `tickets:ver_propios`, `tickets:atender` |
| `tecnico_especializado` | `tickets:ver_propios`, `tickets:atender` |
| `admin` | Todos los scopes |

## Flujo de estados del ticket

```
solicitado → recibido → asignado → en_proceso → en_revision → terminado
```

---

## Evidencias de funcionamiento


- Login y token generado
- Endpoint protegido con token válido → 200
- Acceso sin token → 401
- Usuario sin scope → 403
- Flujo completo del ticket de `solicitado` a `terminado`

---
