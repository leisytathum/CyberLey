from app.database.supabase_client import SupabaseRESTClient
from app.middlewares.roles import invalidate_role_cache


def list_profiles(token: str, limit: int = 500) -> list[dict]:
    db = SupabaseRESTClient(token)
    profiles = db.get_all("perfiles", order="fecha_creacion.desc")
    participants = {x.get("id_usuario"): x for x in db.get_all("participantes")}
    surveys = db.get_all("respuestas_encuesta_ciberseguridad", order="fecha_respuesta.desc")
    by_user: dict[str, list[dict]] = {}
    for row in surveys: by_user.setdefault(row.get("id_usuario"), []).append(row)
    return [{**profile, **{key: value for key, value in participants.get(profile.get("id"), {}).items() if key not in {"id"}}, "encuestas_realizadas": len(by_user.get(profile.get("id"), [])), "ultima_evaluacion": (by_user.get(profile.get("id")) or [{}])[0].get("fecha_respuesta"), "puntaje_riesgo": (by_user.get(profile.get("id")) or [{}])[0].get("puntaje_riesgo"), "clasificacion_riesgo": (by_user.get(profile.get("id")) or [{}])[0].get("clasificacion_riesgo")} for profile in profiles]


def administration_summary(token: str) -> dict:
    db = SupabaseRESTClient(token)
    users = list_profiles(token)
    reports = db.get_all("reportes", order="fecha_generacion.desc")
    activity = sorted([{"fecha": x.get("ultima_evaluacion"), "usuario": x.get("nombre_completo"), "puntaje": x.get("puntaje_riesgo"), "riesgo": x.get("clasificacion_riesgo")} for x in users if x.get("ultima_evaluacion")], key=lambda x: x["fecha"], reverse=True)[:10]
    return {"items": users, "metricas": {"usuarios": len(users), "administradores": sum(x.get("rol") == "admin" for x in users), "participantes": sum(x.get("rol") == "usuario" for x in users), "encuestas": sum(x.get("encuestas_realizadas", 0) for x in users), "reportes": len(reports)}, "actividad": activity, "reportes": reports[:10]}


def change_role(token: str, current_user_id: str, target_id: str, role: str) -> dict:
    if target_id == current_user_id:
        raise ValueError("No puedes cambiar tu propio rol.")
    if role not in {"admin", "usuario"}:
        raise ValueError("Rol inválido.")
    rows = SupabaseRESTClient(token).update("perfiles", {"rol": role}, filters={"id": f"eq.{target_id}"})
    if not rows: raise ValueError("No se encontró el usuario.")
    invalidate_role_cache(target_id)
    return rows[0]
