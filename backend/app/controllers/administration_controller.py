from fastapi import HTTPException

from app.services.administration_service import administration_summary, change_role


def get_profiles(user: dict) -> dict:
    try:
        return administration_summary(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def update_role(target_id: str, role: str, user: dict) -> dict:
    try:
        return change_role(user["token"], user["id"], target_id, role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
