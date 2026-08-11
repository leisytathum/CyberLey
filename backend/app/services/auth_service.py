from app.database.supabase_client import SupabaseRESTClient


def get_profile(user: dict) -> dict | None:
    rows = SupabaseRESTClient(user["token"]).get(
        "perfiles",
        filters={"id": f"eq.{user['id']}"},
        limit=1,
    )
    return rows[0] if rows else None
