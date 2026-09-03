from fastapi import HTTPException, UploadFile

from app.services.backups_service import export_backup, import_backup, inspect_backup
from app.utils.uploads import read_limited_upload


def backup(user: dict) -> dict:
    try:
        return export_backup(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def preview(file: UploadFile) -> dict:
    try:
        content = await read_limited_upload(file, allowed_suffixes={".gz", ".json"}, max_bytes=50 * 1024 * 1024)
        return inspect_backup(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def restore(file: UploadFile, user: dict) -> dict:
    try:
        content = await read_limited_upload(file, allowed_suffixes={".gz", ".json"}, max_bytes=50 * 1024 * 1024)
        return import_backup(user["token"], content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
