from app.database.supabase_client import SupabaseRESTClient


def list_surveys(token: str, limit: int = 500) -> list[dict]:
    return SupabaseRESTClient(token).get(
        "respuestas_encuesta_ciberseguridad",
        limit=limit,
    )
