from fastapi import HTTPException

from app.services.cleaning_service import get_diagnostic


def diagnostic(user: dict) -> dict:
    try:
        return get_diagnostic(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
