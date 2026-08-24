from fastapi import HTTPException

from app.services.cleaning_service import apply_cleaning, get_diagnostic


def diagnostic(user: dict) -> dict:
    try:
        return get_diagnostic(user["token"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def apply(target: str, user: dict) -> dict:
    if target not in {"participantes", "encuestas"}:
        raise HTTPException(status_code=400, detail="Objetivo de limpieza inválido.")
    try:
        return apply_cleaning(user["token"], target)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
