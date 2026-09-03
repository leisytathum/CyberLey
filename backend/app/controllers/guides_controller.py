from fastapi import HTTPException
from app.services.guides_service import complete_guide, list_guides
from app.utils.exceptions import CyberLeyError


def get_guides(user: dict) -> dict:
    try: return list_guides(user["token"], user["id"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def mark_complete(guide_id: str, user: dict) -> dict:
    try: return complete_guide(user["token"], user["id"], guide_id)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc
