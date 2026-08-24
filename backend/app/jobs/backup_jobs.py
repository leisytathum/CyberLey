import gzip
import json
from datetime import datetime

from app.database.supabase_client import SupabaseRESTClient


BACKUP_TABLES = (
    "perfiles",
    "participantes",
    "respuestas_encuesta_ciberseguridad",
    "reportes",
)


def build_backup(token: str) -> dict:
    db = SupabaseRESTClient(token)
    return {
        "metadata": {"sistema": "CyberLey", "version": "2.0", "fecha_generacion": datetime.now().isoformat(), "tablas_incluidas": list(BACKUP_TABLES)},
        "datos": {table: db.get_all(table) for table in BACKUP_TABLES},
    }


def encode_backup(backup: dict) -> bytes:
    return gzip.compress(json.dumps(backup, ensure_ascii=False, default=str).encode("utf-8"))


def decode_backup(content: bytes) -> dict:
    try:
        backup = json.loads(gzip.decompress(content).decode("utf-8"))
    except Exception as exc:
        raise ValueError("El archivo no es un respaldo válido de CyberLey.") from exc
    if backup.get("metadata", {}).get("sistema") != "CyberLey":
        raise ValueError("El archivo no pertenece a CyberLey.")
    data = backup.get("datos", {})
    for table in BACKUP_TABLES:
        if not isinstance(data.get(table), list):
            raise ValueError(f"El respaldo no contiene datos válidos para {table}.")
    return backup


def restore_backup(token: str, backup: dict) -> dict:
    db = SupabaseRESTClient(token)
    conflicts = {"perfiles": "id", "participantes": "id_participante", "respuestas_encuesta_ciberseguridad": "id_respuesta", "reportes": "id_reporte"}
    result = {}
    for table in BACKUP_TABLES:
        rows = backup["datos"][table]
        if rows: db.upsert(table, rows, on_conflict=conflicts[table])
        result[table] = len(rows)
    return result
