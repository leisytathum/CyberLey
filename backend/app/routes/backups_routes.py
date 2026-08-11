from fastapi import APIRouter, Depends

from app.controllers.backups_controller import backup
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/respaldos", tags=["Respaldos"])


@router.get("/exportar")
def export(user: dict = Depends(require_admin)):
    return backup(user)
