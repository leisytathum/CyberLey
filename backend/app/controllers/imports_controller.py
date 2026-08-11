from fastapi import HTTPException, UploadFile

from app.services.imports_service import validate_csv_content


async def validate_csv(archivo: UploadFile) -> dict:
    try:
        return validate_csv_content(archivo.filename or "", await archivo.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
