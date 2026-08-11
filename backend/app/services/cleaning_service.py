import pandas as pd

from app.database.supabase_client import SupabaseRESTClient


def _diagnose(rows: list[dict]) -> dict:
    if not rows:
        return {"registros": 0, "duplicados_aprox": 0, "campos_vacios": 0}

    dataframe = pd.DataFrame(rows)
    return {
        "registros": len(dataframe),
        "duplicados_aprox": int(dataframe.astype(str).duplicated().sum()),
        "campos_vacios": int(dataframe.isna().sum().sum()),
    }


def get_diagnostic(token: str) -> dict:
    db = SupabaseRESTClient(token)
    participants = db.get("participantes", limit=5000)
    surveys = db.get("respuestas_encuesta_ciberseguridad", limit=5000)
    return {
        "participantes": _diagnose(participants),
        "encuestas": _diagnose(surveys),
    }
