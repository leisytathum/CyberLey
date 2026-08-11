from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.logging_config import configure_logging
from app.config.settings import settings
from app.middlewares.error_handler import register_exception_handlers
from app.middlewares.request_logger import RequestLoggerMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.routes.api_router import api_router


configure_logging()
log = logging.getLogger("cyberley")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Iniciando %s", settings.app_name)
    log.info("Entorno: %s", settings.app_env)
    log.info("Frontend permitido: %s", ", ".join(settings.origins))
    log.info(
        "Supabase configurado: %s",
        "sí" if settings.supabase_url and settings.supabase_publishable_key else "NO",
    )
    log.info("Acceso a datos: sesión autenticada + RLS de Supabase")
    yield
    log.info("CyberLey API detenida")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API de CyberLey para React, FastAPI y Supabase.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggerMiddleware)

register_exception_handlers(app)
app.include_router(api_router)


@app.get("/", tags=["Sistema"])
def root():
    return {
        "message": "CyberLey API funcionando",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
