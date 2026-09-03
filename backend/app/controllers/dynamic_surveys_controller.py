"""Casos de uso HTTP para encuestas configurables.

El controlador mantiene las rutas declarativas y traduce fallos de infraestructura
en errores de API estables. Las reglas de negocio permanecen en el servicio.
"""

from collections.abc import Callable
from typing import Any

from app.schemas.dynamic_survey_schema import SurveyCreate, SurveySubmission
from app.services.dynamic_surveys_service import (
    available_surveys,
    change_survey_state,
    create_survey,
    list_admin_surveys,
    published_survey_detail,
    submit_survey,
    survey_detail,
)
from app.utils.exceptions import CyberLeyError, DataAccessError


def _execute(operation: Callable[..., Any], *args) -> Any:
    try:
        return operation(*args)
    except CyberLeyError:
        raise
    except RuntimeError as exc:
        raise DataAccessError("No fue posible consultar la información en este momento.") from exc


def list_for_admin(user: dict) -> dict:
    items = _execute(list_admin_surveys, user["token"])
    return {"items": items, "total": len(items)}


def create_for_admin(payload: SurveyCreate, user: dict) -> dict:
    return _execute(create_survey, user["token"], user["id"], payload)


def detail_for_admin(survey_id: str, user: dict) -> dict:
    return _execute(survey_detail, user["token"], survey_id, True)


def change_state_for_admin(survey_id: str, state: str, user: dict) -> dict:
    return _execute(change_survey_state, user["token"], survey_id, state)


def list_for_user(user: dict) -> dict:
    items = _execute(available_surveys, user["token"], user["id"])
    return {
        "items": items,
        "total": len(items),
        "pendientes": sum(not item.get("respondida") for item in items),
        "completadas": sum(bool(item.get("respondida")) for item in items),
    }


def detail_for_user(survey_id: str, user: dict) -> dict:
    return _execute(published_survey_detail, user["token"], survey_id)


def submit_for_user(survey_id: str, payload: SurveySubmission, user: dict) -> dict:
    return _execute(submit_survey, user["token"], user["id"], survey_id, payload)
