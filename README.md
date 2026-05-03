# Laboratorio 3 — Mesa de Servicios para Laboratorios Universitarios

API REST para gestión de tickets de servicios, construida con FastAPI, PostgreSQL y autenticación JWT con scopes.

---

## Integrantes

| Nombre | Aporte |
|---|---|
| Juan Diego Pérez | `database.py`, `models.py`, `auth.py`, `routers/tickets.py` |
| Valentina Zapata | `schemas.py`, `main.py`, `routers/usuarios.py`, `routers/laboratorios.py`, `routers/servicios.py` |

---

## Descripción del Sistema

API para gestionar solicitudes de servicios en laboratorios universitarios. Permite crear tickets, asignarlos a técnicos y hacer seguimiento del flujo de atención. El acceso está controlado mediante autenticación JWT y autorización basada en scopes según el rol del usuario.

### Entidades implementadas
- **Usuarios** — solicitantes, técnicos, responsables y administradores
- **Laboratorios** — espacios físicos donde se solicita el servicio
- **Servicios** — tipos de soporte disponibles
- **Tickets** — solicitudes de servicio con flujo de estados

---

## Estructura del proyecto

laboratorio3/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── requirements.txt
├── .env               # No incluido en el repositorio
├── .gitignore
├── evidencias/        # Capturas de pantalla de las pruebas
└── routers/
├── init.py
├── auth.py
├── usuarios.py
├── laboratorios.py
├── servicios.py
└── tickets.py
---

## Configuración del Entorno

**1. Clonar el repositorio y crear el entorno virtual**

```bash
git clone https://github.com/Juanperezp/laboratorio3.git
cd laboratorio3
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
```

**2. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**3. Crear el archivo `.env`**

```env
DATABASE_URL=postgresql://usuario:contraseña@host:5432/dbapps?options=-csearch_path%3Dnombre_schema
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**4. Ejecutar**

```bash
uvicorn main:app --reload
```

Swagger disponible en: http://localhost:8000/docs

---

## Configuración de la Base de Datos

- Motor: PostgreSQL
- ORM: SQLAlchemy
- Schema asignado: `jwt_grupo_10`
- Las tablas se crean automáticamente al iniciar la API con `Base.metadata.create_all(bind=engine)`

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

## Roles y Scopes

| Rol | Scopes |
|---|---|
| `solicitante` | `tickets:crear`, `tickets:ver_propios` |
| `responsable_tecnico` | `tickets:ver_propios`, `tickets:recibir`, `tickets:asignar`, `tickets:finalizar` |
| `auxiliar` | `tickets:ver_propios`, `tickets:atender` |
| `tecnico_especializado` | `tickets:ver_propios`, `tickets:atender` |
| `admin` | Todos los scopes |

---

## Flujo de Estados del Ticket

solicitado → recibido → asignado → en_proceso → en_revision → terminado
| Transición | Quién puede realizarla | Scope requerido |
|---|---|---|
| `solicitado` → `recibido` | responsable_tecnico, admin | `tickets:recibir` |
| `recibido` → `asignado` | responsable_tecnico, admin | `tickets:asignar` |
| `asignado` → `en_proceso` | auxiliar/tecnico asignado, admin | `tickets:atender` |
| `en_proceso` → `en_revision` | auxiliar/tecnico asignado, admin | `tickets:atender` |
| `en_revision` → `terminado` | responsable_tecnico, admin | `tickets:finalizar` |

---

## Evidencias de Funcionamiento

### Creación de Usuarios

#### Crear usuario solicitante
![Crear usuario solicitante](evidencias/crear_usuario_solicitante.PNG)

#### Crear usuario responsable técnico
![Crear usuario responsable](evidencias/tecnico_responsable.PNG)

#### Crear usuario auxiliar
![Crear usuario auxiliar](evidencias/crear_usuario_auxiliar.PNG)

#### Crear usuario técnico especializado
![Crear usuario tecnico](evidencias/usuario_técnico_especializado.PNG)

---

### Autenticación JWT

#### Login exitoso con token generado
![Login exitoso](evidencias/login_solicitante.PNG)

#### Acceso sin token — HTTP 401
![Acceso sin token](evidencias/Acceso_sin_token.PNG)

---

### Autorización con Scopes

#### Solicitante intenta asignar ticket — HTTP 403
![Sin scope 403](evidencias/Solicitante intenta asignar ticket (debe dar 403).PNG)

---

### Reglas de Negocio del Ticket

#### Solicitante crea ticket — HTTP 201
![Crear ticket](evidencias/Solicitante_crea_ticket.PNG)

#### Responsable técnico asigna ticket
![Asignar ticket](evidencias/técnico_asigna_ticket.PNG)

#### Estado del ticket
![Estado ticket](evidencias/estado ticket.PNG)

#### Laboratorio creado
![Laboratorio](evidencias/creacion_laboratorios.PNG)

#### Listar servicios
![Servicio](evidencias/listar_servicios.PNG)
## Control de Versiones


- Repositorio: https://github.com/Juanperezp/laboratorio3
- Rama principal: `main`
- Rama de desarrollo: `database-auth`

### Aportes por integrante

| Integrante | Commits | Archivos |
|---|---|---|
| Juan Diego Pérez | `database.py`, `models.py`, `auth.py`, `routers/tickets.py` | Backend core y seguridad |
| Valentina Zapata | `schemas.py`, `main.py`, `routers/usuarios.py`, `routers/laboratorios.py`, `routers/servicios.py` | Schemas y endpoints |

---

## Conclusiones

- Se implementó autenticación segura con JWT y hashing bcrypt de contraseñas.
- Los scopes permiten controlar el acceso a cada endpoint de forma granular según el rol del usuario.
- El flujo de estados del ticket garantiza que solo los usuarios autorizados puedan realizar cada transición.
- El trabajo colaborativo con Git y GitHub permitió dividir el desarrollo de forma organizada.
- Se presentaron dificultades al integrar los schemas de ambos integrantes por diferencias en los nombres de las clases, lo cual se resolvió mediante alias y ajustes en los modelos.

---

## Bibliografía

- FastAPI. (2024). *FastAPI Documentation*. https://fastapi.tiangolo.com
- FastAPI. (2024). *OAuth2 with scopes*. https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
- Pydantic. (2024). *Pydantic Documentation*. https://docs.pydantic.dev