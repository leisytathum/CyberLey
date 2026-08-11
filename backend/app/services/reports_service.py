from app.database.supabase_client import SupabaseRESTClient


def list_reports(token: str, limit: int = 500) -> list[dict]:
    return SupabaseRESTClient(token).get("reportes", limit=limit)
