from fastapi import HTTPException

from app.services.reports_service import list_reports


def get_reports(user: dict) -> dict:
    try:
        items = list_reports(user["token"])
        return {"items": items, "total": len(items)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
