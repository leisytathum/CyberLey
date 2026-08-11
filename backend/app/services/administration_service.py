from app.database.supabase_client import SupabaseRESTClient


def list_profiles(token: str, limit: int = 500) -> list[dict]:
    return SupabaseRESTClient(token).get("perfiles", limit=limit)
