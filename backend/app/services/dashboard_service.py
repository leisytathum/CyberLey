from app.database.supabase_client import SupabaseRESTClient


def get_summary(token: str) -> dict:
    db = SupabaseRESTClient(token)
    return {
        "participantes": db.count("participantes"),
        "encuestas": db.count("respuestas_encuesta_ciberseguridad"),
        "reportes": db.count("reportes"),
        "riesgo_alto": db.count(
            "respuestas_encuesta_ciberseguridad",
            {"clasificacion_riesgo": "eq.alto"},
        ),
    }
