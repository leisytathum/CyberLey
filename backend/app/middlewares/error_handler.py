import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.exceptions import CyberLeyError


log = logging.getLogger("cyberley.error")


def register_exception_handlers(app) -> None:
    @app.exception_handler(CyberLeyError)
    async def domain_error(request: Request, exc: CyberLeyError):
        log.warning("Error de dominio en %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        log.exception("Error no controlado en %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Ocurrió un error interno en CyberLey API.",
                "code": "internal_error",
            },
        )
