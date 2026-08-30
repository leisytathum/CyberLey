from datetime import datetime, timezone
from app.database.supabase_client import SupabaseRESTClient
from app.schemas.dynamic_survey_schema import SurveyCreate, SurveySubmission

def _questions(db, survey_id):
    return db.get_all("preguntas_dinamicas", filters={"id_encuesta": f"eq.{survey_id}"}, order="orden.asc")

def create_survey(token: str, user_id: str, payload: SurveyCreate) -> dict:
    db = SupabaseRESTClient(token)
    survey = db.insert("encuestas_dinamicas", {"titulo": payload.titulo.strip(), "descripcion": payload.descripcion.strip(), "creada_por": user_id})[0]
    for order, question in enumerate(payload.preguntas, 1):
        db.insert("preguntas_dinamicas", {"id_encuesta": survey["id"], "texto": question.texto.strip(), "tipo": question.tipo, "requerida": question.requerida, "orden": order, "opciones": [option.model_dump() for option in question.opciones]})
    return {**survey, "preguntas": _questions(db, survey["id"])}

def list_admin_surveys(token: str) -> list[dict]:
    db = SupabaseRESTClient(token)
    surveys = db.get_all("encuestas_dinamicas", order="fecha_creacion.desc")
    applications = db.get_all("aplicaciones_encuesta")
    questions = db.get_all("preguntas_dinamicas")
    return [{**survey, "total_preguntas": sum(row.get("id_encuesta") == survey["id"] for row in questions), "total_respuestas": sum(row.get("id_encuesta") == survey["id"] for row in applications)} for survey in surveys]

def survey_detail(token: str, survey_id: str, include_answers: bool = False) -> dict:
    db = SupabaseRESTClient(token)
    rows = db.get("encuestas_dinamicas", filters={"id": f"eq.{survey_id}"}, limit=1)
    if not rows: raise ValueError("Encuesta no encontrada.")
    result = {**rows[0], "preguntas": _questions(db, survey_id)}
    if include_answers:
        profiles = {row["id"]: row for row in db.get_all("perfiles")}
        participants = {row.get("id_usuario"): row for row in db.get_all("participantes")}
        result["aplicaciones"] = [{**row, "nombre_usuario": participants.get(row.get("id_usuario"), {}).get("nombre_completo") or profiles.get(row.get("id_usuario"), {}).get("nombre_completo") or "Usuario"} for row in db.get_all("aplicaciones_encuesta", filters={"id_encuesta": f"eq.{survey_id}"}, order="fecha_respuesta.asc")]
    return result

def change_survey_state(token: str, survey_id: str, state: str) -> dict:
    payload = {"estado": state}
    if state == "publicada": payload["fecha_publicacion"] = datetime.now(timezone.utc).isoformat()
    rows = SupabaseRESTClient(token).update("encuestas_dinamicas", payload, filters={"id": f"eq.{survey_id}"})
    if not rows: raise ValueError("Encuesta no encontrada.")
    return rows[0]

def available_surveys(token: str, user_id: str) -> list[dict]:
    db = SupabaseRESTClient(token)
    completed = {row.get("id_encuesta") for row in db.get_all("aplicaciones_encuesta", filters={"id_usuario": f"eq.{user_id}"})}
    return [{**row, "respondida": row["id"] in completed, "total_preguntas": len(_questions(db, row["id"]))} for row in db.get_all("encuestas_dinamicas", filters={"estado": "eq.publicada"}, order="fecha_publicacion.desc")]

def submit_survey(token: str, user_id: str, survey_id: str, payload: SurveySubmission) -> dict:
    db = SupabaseRESTClient(token)
    survey = survey_detail(token, survey_id)
    if survey["estado"] != "publicada": raise ValueError("Esta encuesta no está disponible.")
    questions = {row["id"]: row for row in survey["preguntas"]}
    submitted = {row.id_pregunta: row.valor for row in payload.respuestas}
    if any(question["requerida"] and question_id not in submitted for question_id, question in questions.items()): raise ValueError("Completa todas las preguntas requeridas.")
    answers, score, maximum = [], 0, 0
    for question_id, question in questions.items():
        value = submitted.get(question_id)
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
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower(): raise ValueError("Ya respondiste esta encuesta.") from exc
        raise
    return row
