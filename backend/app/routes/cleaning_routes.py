from fastapi import APIRouter, Depends

from app.controllers.cleaning_controller import apply, diagnostic
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/limpieza", tags=["Limpieza"])


@router.get("/diagnostico")
def cleaning_diagnostic(user: dict = Depends(require_admin)):
    return diagnostic(user)


@router.post("/aplicar/{target}")
def cleaning_apply(target: str, user: dict = Depends(require_admin)):
    return apply(target, user)
