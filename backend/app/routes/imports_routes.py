from fastapi import APIRouter, Depends, File, UploadFile

from app.controllers.imports_controller import validate_csv
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/importaciones", tags=["Importaciones"])


@router.post("/csv")
async def csv_import(
    archivo: UploadFile = File(...),
    user: dict = Depends(require_admin),
):
    return await validate_csv(archivo)
