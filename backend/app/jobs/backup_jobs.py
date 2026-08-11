from app.database.supabase_client import SupabaseRESTClient


BACKUP_TABLES = (
    "perfiles",
    "participantes",
    "respuestas_encuesta_ciberseguridad",
    "reportes",
)


def build_backup(token: str) -> dict:
    db = SupabaseRESTClient(token)
    return {table: db.get(table, limit=10000) for table in BACKUP_TABLES}
