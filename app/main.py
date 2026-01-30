from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import get_settings
from app.core.database import Base, engine
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
