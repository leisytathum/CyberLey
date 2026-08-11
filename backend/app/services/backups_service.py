from app.jobs.backup_jobs import build_backup


def export_backup(token: str) -> dict:
    return build_backup(token)
