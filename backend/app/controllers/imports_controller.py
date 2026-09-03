from fastapi import HTTPException, UploadFile

from app.services.imports_service import validate_csv_content
from app.utils.uploads import read_limited_upload


async def validate_csv(archivo: UploadFile) -> dict:
    try:
        content = await read_limited_upload(archivo, allowed_suffixes={".csv"}, max_bytes=10 * 1024 * 1024)
        return validate_csv_content(archivo.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
