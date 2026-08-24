from fastapi import HTTPException, UploadFile

from app.services.backups_service import export_backup, import_backup, inspect_backup


def backup(user: dict) -> dict:
    try:
        return export_backup(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def preview(file: UploadFile) -> dict:
    try:
        return inspect_backup(await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def restore(file: UploadFile, user: dict) -> dict:
    try:
        return import_backup(user["token"], await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
