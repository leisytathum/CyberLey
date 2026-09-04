from fastapi import HTTPException
from app.services.guides_service import assign_guide, complete_guide, create_guide, delete_guide, list_admin_guides, list_guides, update_guide
from app.utils.exceptions import CyberLeyError


def get_guides(user: dict) -> dict:
    try: return list_guides(user["token"], user["id"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def mark_complete(guide_id: str, user: dict) -> dict:
    try: return complete_guide(user["token"], user["id"], guide_id)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def get_admin_guides(user: dict) -> dict:
    try: return list_admin_guides(user["token"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def create_for_admin(payload, file_data, user: dict) -> dict:
    try: return create_guide(user["token"], user["id"], payload, file_data)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def assign_for_admin(guide_id: str, payload, user: dict) -> dict:
    try: return assign_guide(user["token"], guide_id, payload)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def update_for_admin(guide_id: str, payload, user: dict) -> dict:
    try: return update_guide(user["token"], guide_id, payload)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


def delete_for_admin(guide_id: str, user: dict) -> dict:
    try: return delete_guide(user["token"], guide_id)
    except CyberLeyError: raise
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc
