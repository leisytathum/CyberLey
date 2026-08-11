from fastapi import HTTPException

from app.services.administration_service import list_profiles


def get_profiles(user: dict) -> dict:
    try:
        items = list_profiles(user["token"])
        return {"items": items, "total": len(items)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
