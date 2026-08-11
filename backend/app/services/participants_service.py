from app.database.supabase_client import SupabaseRESTClient


def list_participants(token: str, limit: int = 500) -> list[dict]:
    return SupabaseRESTClient(token).get("participantes", limit=limit)
