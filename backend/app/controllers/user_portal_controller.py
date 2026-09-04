from app.services.user_portal_service import build_user_summary, complete_user_onboarding
from app.services.assistant_service import answer_user_question
from app.schemas.assistant_schema import AssistantQuestion
from app.utils.exceptions import DataAccessError


def get_user_summary(user: dict) -> dict:
    try:
        return build_user_summary(user["token"], user["id"])
    except RuntimeError as exc:
        raise DataAccessError("No fue posible preparar el resumen de tu cuenta.") from exc


def finish_user_onboarding(user: dict) -> dict:
    try:
        return complete_user_onboarding(user["token"])
    except RuntimeError as exc:
        raise DataAccessError("No fue posible guardar el estado del recorrido inicial.") from exc


def ask_assistant(payload: AssistantQuestion, user: dict) -> dict:
    try:
        history = [message.model_dump() for message in payload.historial]
        return answer_user_question(user["token"], user["id"], payload.pregunta, history)
    except RuntimeError as exc:
        raise DataAccessError("Ciby no pudo consultar tu información en este momento.") from exc
