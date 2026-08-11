from fastapi import HTTPException

from app.services.backups_service import export_backup


def backup(user: dict) -> dict:
    try:
        return export_backup(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
