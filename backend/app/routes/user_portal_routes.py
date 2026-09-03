from fastapi import APIRouter, Depends

from app.controllers.user_portal_controller import ask_assistant, finish_user_onboarding, get_user_summary
from app.middlewares.auth import current_user
from app.schemas.assistant_schema import AssistantQuestion


router = APIRouter(prefix="/usuario", tags=["Portal de usuario"])


@router.get("/resumen", summary="Obtener el resumen personalizado del usuario")
def summary(user: dict = Depends(current_user)):
    return get_user_summary(user)


@router.post("/onboarding/completar", summary="Guardar la finalización del recorrido inicial")
def complete_onboarding(user: dict = Depends(current_user)):
    return finish_user_onboarding(user)


@router.post("/asistente", summary="Consultar a Ciby sobre CyberLey y seguridad digital")
def assistant(payload: AssistantQuestion, user: dict = Depends(current_user)):
    return ask_assistant(payload, user)
