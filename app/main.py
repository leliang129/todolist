from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import get_settings
from sqlalchemy import inspect, text
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.crud.user import get_user_by_username, create_user
from app.api.routes import auth, users, categories, todos, trash, stats

settings = get_settings()

app = FastAPI(title="Todo API", version="0.1.0")

origins = settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")
app.include_router(trash.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

# Serve built frontend (single container deployment)
static_dir = Path(__file__).resolve().parents[1] / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.exception_handler(FastAPIHTTPException)
def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    mapping = {401: 40101, 403: 40301, 404: 40401}
    code = mapping.get(exc.status_code, 40001)
    message = exc.detail if isinstance(exc.detail, str) else "error"
    return JSONResponse(status_code=exc.status_code, content={"code": code, "message": message, "data": {}})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": 40001, "message": "validation_error", "data": exc.errors()})


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_user_role_column()
    ensure_superadmin()


def ensure_user_role_column():
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = [col["name"] for col in inspector.get_columns("users")]
    if "role" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT 'user'"))


def ensure_superadmin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "superadmin").first()
        if user:
            return
        existing = get_user_by_username(db, settings.admin_username)
        if existing:
            existing.role = "superadmin"
            db.add(existing)
            db.commit()
            return
        create_user(
            db,
            settings.admin_username,
            settings.admin_password,
            settings.admin_email,
            role="superadmin",
        )
    finally:
        db.close()
