from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from app.database.supabase_client import SupabaseRESTClient


def list_participants(token: str) -> list[dict]:
    db = SupabaseRESTClient(token)
    with ThreadPoolExecutor(max_workers=3) as executor:
        participants_future = executor.submit(
            db.get_all, "participantes", order="fecha_registro.desc"
        )
        profiles_future = executor.submit(db.get_all, "perfiles")
        surveys_future = executor.submit(
            db.get_all,
            "respuestas_encuesta_ciberseguridad",
            order="fecha_respuesta.desc",
        )
        participants = participants_future.result()
        profiles = {row["id"]: row for row in profiles_future.result()}
        surveys = surveys_future.result()
    by_user: dict[str, list[dict]] = {}
    for survey in surveys:
        by_user.setdefault(survey.get("id_usuario"), []).append(survey)
    result = []
    for participant in participants:
        if profiles.get(participant.get("id_usuario"), {}).get("rol") != "usuario":
            continue
        evaluations = by_user.get(participant.get("id_usuario"), [])
        latest = evaluations[0] if evaluations else {}
        result.append({
            **participant,
            "encuestas_realizadas": len(evaluations),
            "fecha_ultima_evaluacion": latest.get("fecha_respuesta"),
            "puntaje_riesgo": latest.get("puntaje_riesgo"),
            "clasificacion_riesgo": latest.get("clasificacion_riesgo") or "sin_evaluar",
            "nivel_conocimiento": latest.get("nivel_conocimiento"),
            "reconoce_phishing": latest.get("reconoce_phishing"),
            "estado_antivirus": latest.get("estado_antivirus"),
            "reutiliza_contrasenas": latest.get("reutiliza_contrasenas"),
            "tipo_conexion": latest.get("tipo_conexion"),
            "observacion": latest.get("observacion"),
        })
    return result


def participant_statistics(items: list[dict]) -> dict:
    scores = [x["puntaje_riesgo"] for x in items if isinstance(x.get("puntaje_riesgo"), (int, float))]
    evaluated = sum(x.get("encuestas_realizadas", 0) > 0 for x in items)
    return {
        "total": len(items), "evaluados": evaluated, "pendientes": len(items) - evaluated,
        "riesgo_alto": sum(x.get("clasificacion_riesgo") == "alto" for x in items),
        "promedio_riesgo": round(sum(scores) / len(scores), 1) if scores else 0,
    }
