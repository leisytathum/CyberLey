from fastapi import HTTPException

from app.services.participants_service import list_participants


def get_participants(user: dict) -> dict:
    try:
        items = list_participants(user["token"])
        return {"items": items, "total": len(items)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
