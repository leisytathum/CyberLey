import logging

from fastapi import Request
from fastapi.responses import JSONResponse


log = logging.getLogger("cyberley.error")


def register_exception_handlers(app) -> None:
    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        log.exception("Error no controlado en %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Ocurrió un error interno en CyberLey API."},
        )
