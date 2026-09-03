from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from app.database.supabase_client import SupabaseRESTClient
from app.schemas.dynamic_survey_schema import SurveyCreate, SurveySubmission
from app.utils.exceptions import BusinessValidationError, ConflictError, ResourceNotFoundError

def _questions(db: SupabaseRESTClient, survey_id: str) -> list[dict]:
    return db.get_all("preguntas_dinamicas", filters={"id_encuesta": f"eq.{survey_id}"}, order="orden.asc")


def _survey_or_fail(db: SupabaseRESTClient, survey_id: str) -> dict:
    rows = db.get("encuestas_dinamicas", filters={"id": f"eq.{survey_id}"}, limit=1)
    if not rows:
        raise ResourceNotFoundError("Encuesta no encontrada.")
    return rows[0]


def _validated_value(question: dict, value):
    question_type = question.get("tipo")
    if question_type == "texto":
        if not isinstance(value, str):
            raise BusinessValidationError("Las respuestas de texto deben ser cadenas de caracteres.")
        value = value.strip()
        if question.get("requerida") and not value:
            raise BusinessValidationError("Completa todas las preguntas requeridas.")
        if len(value) > 2000:
            raise BusinessValidationError("Una respuesta de texto no puede superar 2000 caracteres.")
        return value

    allowed = {str(option.get("etiqueta")) for option in (question.get("opciones") or [])}
    if str(value) not in allowed:
        raise BusinessValidationError(f"La respuesta para «{question.get('texto')}» no es una opción válida.")
    return value

def create_survey(token: str, user_id: str, payload: SurveyCreate) -> dict:
    db = SupabaseRESTClient(token)
    survey = db.insert("encuestas_dinamicas", {"titulo": payload.titulo.strip(), "descripcion": payload.descripcion.strip(), "creada_por": user_id})[0]
    try:
        for order, question in enumerate(payload.preguntas, 1):
            db.insert("preguntas_dinamicas", {"id_encuesta": survey["id"], "texto": question.texto, "tipo": question.tipo, "requerida": question.requerida, "orden": order, "opciones": [option.model_dump() for option in question.opciones]})
    except Exception:
        db.delete("encuestas_dinamicas", filters={"id": f"eq.{survey['id']}"})
        raise
    return {**survey, "preguntas": _questions(db, survey["id"])}

def list_admin_surveys(token: str) -> list[dict]:
    db = SupabaseRESTClient(token)
    with ThreadPoolExecutor(max_workers=3) as executor:
        surveys_future = executor.submit(db.get_all, "encuestas_dinamicas", order="fecha_creacion.desc")
        applications_future = executor.submit(db.get_all, "aplicaciones_encuesta")
        questions_future = executor.submit(db.get_all, "preguntas_dinamicas")
        surveys = surveys_future.result()
        applications = applications_future.result()
        questions = questions_future.result()
    return [{**survey, "total_preguntas": sum(row.get("id_encuesta") == survey["id"] for row in questions), "total_respuestas": sum(row.get("id_encuesta") == survey["id"] for row in applications)} for survey in surveys]

def survey_detail(token: str, survey_id: str, include_answers: bool = False) -> dict:
    db = SupabaseRESTClient(token)
    survey = _survey_or_fail(db, survey_id)
    result = {**survey, "preguntas": _questions(db, survey_id)}
    if include_answers:
        profiles = {row["id"]: row for row in db.get_all("perfiles")}
        participants = {row.get("id_usuario"): row for row in db.get_all("participantes")}
        result["aplicaciones"] = [{**row, "nombre_usuario": participants.get(row.get("id_usuario"), {}).get("nombre_completo") or profiles.get(row.get("id_usuario"), {}).get("nombre_completo") or "Usuario"} for row in db.get_all("aplicaciones_encuesta", filters={"id_encuesta": f"eq.{survey_id}"}, order="fecha_respuesta.asc")]
    return result


def published_survey_detail(token: str, survey_id: str) -> dict:
    result = survey_detail(token, survey_id)
    if result.get("estado") != "publicada":
        raise ResourceNotFoundError("La encuesta no está disponible.")
    return result

def change_survey_state(token: str, survey_id: str, state: str) -> dict:
    payload = {"estado": state}
    if state == "publicada": payload["fecha_publicacion"] = datetime.now(timezone.utc).isoformat()
    db = SupabaseRESTClient(token)
    current = _survey_or_fail(db, survey_id)
    if current.get("estado") == state:
        return current
    if state == "publicada" and not _questions(db, survey_id):
        raise BusinessValidationError("No puedes publicar una encuesta sin preguntas.")
    rows = db.update("encuestas_dinamicas", payload, filters={"id": f"eq.{survey_id}"})
    if not rows: raise ResourceNotFoundError("Encuesta no encontrada.")
    return rows[0]

def available_surveys(token: str, user_id: str) -> list[dict]:
    db = SupabaseRESTClient(token)
    with ThreadPoolExecutor(max_workers=3) as executor:
        completed_future = executor.submit(db.get_all, "aplicaciones_encuesta", filters={"id_usuario": f"eq.{user_id}"})
        surveys_future = executor.submit(db.get_all, "encuestas_dinamicas", filters={"estado": "eq.publicada"}, order="fecha_publicacion.desc")
        questions_future = executor.submit(db.get_all, "preguntas_dinamicas", select="id,id_encuesta")
        completed = {row.get("id_encuesta") for row in completed_future.result()}
        surveys = surveys_future.result()
        question_counts: dict[str, int] = {}
        for question in questions_future.result():
            survey_id = question.get("id_encuesta")
            question_counts[survey_id] = question_counts.get(survey_id, 0) + 1
    return [{**row, "respondida": row["id"] in completed, "total_preguntas": question_counts.get(row["id"], 0)} for row in surveys]

def submit_survey(token: str, user_id: str, survey_id: str, payload: SurveySubmission) -> dict:
    db = SupabaseRESTClient(token)
    survey = published_survey_detail(token, survey_id)
    questions = {row["id"]: row for row in survey["preguntas"]}
    if not questions:
        raise BusinessValidationError("Esta encuesta no contiene preguntas.")
    if db.get("aplicaciones_encuesta", filters={"id_encuesta": f"eq.{survey_id}", "id_usuario": f"eq.{user_id}"}, limit=1):
        raise ConflictError("Ya respondiste esta encuesta.")
    submitted = {str(row.id_pregunta): row.valor for row in payload.respuestas}
    unknown = set(submitted) - set(questions)
    if unknown:
        raise BusinessValidationError("La respuesta contiene preguntas que no pertenecen a esta encuesta.")
    if any(question["requerida"] and (question_id not in submitted or submitted[question_id] in (None, "")) for question_id, question in questions.items()):
        raise BusinessValidationError("Completa todas las preguntas requeridas.")
    answers, score, maximum = [], 0, 0
    for question_id, question in questions.items():
        value = submitted.get(question_id)
        if value is not None:
            value = _validated_value(question, value)
        options = question.get("opciones") or []
        points = next((int(option.get("puntos", 0)) for option in options if str(option.get("etiqueta")) == str(value)), 0)
        score += points; maximum += max([int(option.get("puntos", 0)) for option in options] or [0])
        answers.append({"id_pregunta": question_id, "pregunta": question["texto"], "valor": value, "puntos": points, "orden": question["orden"]})
    percentage = round(score * 100 / maximum, 2) if maximum else 0
    classification = "alto" if percentage >= 70 else "medio" if percentage >= 35 else "bajo"
    observation = {"alto": "Se identificaron hábitos que requieren atención prioritaria.", "medio": "Existen prácticas que pueden fortalecerse para reducir el riesgo.", "bajo": "Las respuestas reflejan prácticas generalmente seguras."}[classification]
    try:
        row = db.insert("aplicaciones_encuesta", {"id_encuesta": survey_id, "id_usuario": user_id, "respuestas": answers, "puntaje": score, "puntaje_maximo": maximum, "porcentaje_riesgo": percentage, "clasificacion_riesgo": classification, "observacion": observation})[0]
    except RuntimeError as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower(): raise ConflictError("Ya respondiste esta encuesta.") from exc
        raise
    return row
