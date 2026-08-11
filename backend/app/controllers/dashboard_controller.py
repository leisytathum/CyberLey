from fastapi import HTTPException

from app.services.dashboard_service import get_summary


def summary(user: dict) -> dict:
    try:
        return get_summary(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
