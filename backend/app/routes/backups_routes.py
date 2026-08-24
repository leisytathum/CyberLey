from fastapi import APIRouter, Depends, File, UploadFile

from app.controllers.backups_controller import backup, preview, restore
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/respaldos", tags=["Respaldos"])


@router.get("/exportar")
def export(user: dict = Depends(require_admin)):
    return backup(user)


@router.post("/previsualizar")
async def backup_preview(archivo: UploadFile = File(...), user: dict = Depends(require_admin)):
    return await preview(archivo)


@router.post("/restaurar")
async def backup_restore(archivo: UploadFile = File(...), user: dict = Depends(require_admin)):
    return await restore(archivo, user)
