from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.controllers.dynamic_surveys_controller import (
    change_state_for_admin,
    create_for_admin,
    detail_for_admin,
    detail_for_user,
    list_for_admin,
    list_for_user,
    submit_for_user,
)
from app.middlewares.auth import current_user
from app.middlewares.roles import require_admin
from app.schemas.dynamic_survey_schema import SurveyCreate, SurveyState, SurveySubmission

router = APIRouter(prefix="/encuestas-configurables", tags=["Encuestas configurables"])


@router.get("", summary="Listar encuestas para administración")
def admin_list(user: dict = Depends(require_admin)):
    return list_for_admin(user)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear una encuesta")
def create(payload: SurveyCreate, user: dict = Depends(require_admin)):
    return create_for_admin(payload, user)


@router.get("/disponibles", summary="Listar evaluaciones disponibles para el usuario")
def available(user: dict = Depends(current_user)):
    return list_for_user(user)


@router.get("/admin/{survey_id}", summary="Consultar encuesta y aplicaciones")
def admin_detail(survey_id: UUID, user: dict = Depends(require_admin)):
    return detail_for_admin(str(survey_id), user)


@router.get("/{survey_id}", summary="Consultar una evaluación publicada")
def detail(survey_id: UUID, user: dict = Depends(current_user)):
    return detail_for_user(str(survey_id), user)


@router.patch("/{survey_id}/estado", summary="Cambiar el estado de una encuesta")
def state(survey_id: UUID, payload: SurveyState, user: dict = Depends(require_admin)):
    return change_state_for_admin(str(survey_id), payload.estado, user)


@router.post("/{survey_id}/responder", status_code=status.HTTP_201_CREATED, summary="Registrar una evaluación")
def answer(survey_id: UUID, payload: SurveySubmission, user: dict = Depends(current_user)):
    return submit_for_user(str(survey_id), payload, user)
