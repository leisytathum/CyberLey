from fastapi import APIRouter, Depends, HTTPException
from app.middlewares.auth import current_user
from app.middlewares.roles import require_admin
from app.schemas.dynamic_survey_schema import SurveyCreate, SurveyState, SurveySubmission
from app.services.dynamic_surveys_service import available_surveys, change_survey_state, create_survey, list_admin_surveys, submit_survey, survey_detail

router = APIRouter(prefix="/encuestas-configurables", tags=["Encuestas configurables"])

def call(function, *args):
    try: return function(*args)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get("")
def admin_list(user: dict = Depends(require_admin)): return {"items": call(list_admin_surveys, user["token"])}
@router.post("", status_code=201)
def create(payload: SurveyCreate, user: dict = Depends(require_admin)): return call(create_survey, user["token"], user["id"], payload)
@router.get("/disponibles")
def available(user: dict = Depends(current_user)): return {"items": call(available_surveys, user["token"], user["id"])}
@router.get("/{survey_id}")
def detail(survey_id: str, user: dict = Depends(current_user)): return call(survey_detail, user["token"], survey_id, True)
@router.patch("/{survey_id}/estado")
def state(survey_id: str, payload: SurveyState, user: dict = Depends(require_admin)): return call(change_survey_state, user["token"], survey_id, payload.estado)
@router.post("/{survey_id}/responder", status_code=201)
def answer(survey_id: str, payload: SurveySubmission, user: dict = Depends(current_user)): return call(submit_survey, user["token"], user["id"], survey_id, payload)
