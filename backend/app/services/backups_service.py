import base64
from datetime import datetime

from app.jobs.backup_jobs import build_backup, decode_backup, encode_backup, restore_backup


def export_backup(token: str) -> dict:
    backup = build_backup(token)
    return {
        "archivo": f"backup_cyberley_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.gz",
        "contenido_base64": base64.b64encode(encode_backup(backup)).decode("ascii"),
        "metadata": backup["metadata"],
        "conteos": {table: len(rows) for table, rows in backup["datos"].items()},
    }


def inspect_backup(content: bytes) -> dict:
    backup = decode_backup(content)
    return {"metadata": backup["metadata"], "conteos": {table: len(rows) for table, rows in backup["datos"].items()}}


def import_backup(token: str, content: bytes) -> dict:
    return restore_backup(token, decode_backup(content))
