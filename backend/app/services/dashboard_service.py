from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from app.database.supabase_client import SupabaseRESTClient


def get_summary(token: str) -> dict:
    db = SupabaseRESTClient(token)

    with ThreadPoolExecutor(max_workers=3) as executor:
        profiles_future = executor.submit(db.get_all, "perfiles")
        participants_future = executor.submit(db.get_all, "participantes")
        surveys_future = executor.submit(
            db.get_all,
            "respuestas_encuesta_ciberseguridad",
            order="fecha_respuesta.desc",
        )
        profiles = profiles_future.result()
        all_participants = participants_future.result()
        all_surveys = surveys_future.result()

    roles = {row.get("id"): row.get("rol") for row in profiles}
    participants = [row for row in all_participants if roles.get(row.get("id_usuario")) == "usuario"]

    surveys = [
        row
        for row in all_surveys
        if roles.get(row.get("id_usuario")) == "usuario"
    ]

    total_participants = len(participants)
    total_surveys = len(surveys)

    risk_counter = Counter(
        (
            survey.get("clasificacion_riesgo")
            or ""
        ).lower()
        for survey in surveys
    )

    low_count = risk_counter.get("bajo", 0)
    medium_count = risk_counter.get("medio", 0)
    high_count = risk_counter.get("alto", 0)

    if total_surveys:
        low_percentage = round(
            (low_count / total_surveys) * 100
        )

        medium_percentage = round(
            (medium_count / total_surveys) * 100
        )

        high_percentage = round(
            (high_count / total_surveys) * 100
        )
    else:
        low_percentage = 0
        medium_percentage = 0
        high_percentage = 0

    risk_values = {
        "Bajo": low_count,
        "Medio": medium_count,
        "Alto": high_count,
    }

    if total_surveys:
        predominant_risk = max(
            risk_values,
            key=risk_values.get,
        )

        if risk_values[predominant_risk] == 0:
            predominant_risk = "Sin datos"
    else:
        predominant_risk = "Sin datos"

    reused_passwords = sum(
        1
        for survey in surveys
        if survey.get("reutiliza_contrasenas")
        in {"Sí", "A veces"}
    )

    passwords_not_updated = sum(
        1
        for survey in surveys
        if survey.get(
            "cambio_contrasenas_anual"
        )
        in {
            "Nunca",
            "Una vez al año",
        }
    )

    phishing_difficulty = sum(
        1
        for survey in surveys
        if survey.get("reconoce_phishing")
        in {"No", "A veces"}
    )

    outdated_antivirus = sum(
        1
        for survey in surveys
        if survey.get("estado_antivirus")
        in {
            "No tengo antivirus",
            "Tengo antivirus, pero no está actualizado",
            "No sé",
        }
    )

    def percentage(value: int) -> int:
        if not total_surveys:
            return 0

        return round(
            (value / total_surveys) * 100
        )

    profiles_by_id = {
        profile.get("id"): profile
        for profile in profiles
    }

    recent = []

    for survey in surveys[:5]:
        profile = profiles_by_id.get(
            survey.get("id_usuario"),
            {},
        )

        recent.append(
            {
                "id": survey.get(
                    "id_respuesta"
                ),
                "nombre": profile.get(
                    "nombre_completo",
                    "Usuario",
                ),
                "puntaje": survey.get(
                    "puntaje_riesgo"
                ),
                "clasificacion": survey.get(
                    "clasificacion_riesgo"
                ),
                "fecha": survey.get(
                    "fecha_respuesta"
                ),
            }
        )

    participant_user_ids = {row.get("id_usuario") for row in participants}
    evaluated_participants = {row.get("id_usuario") for row in surveys if row.get("id_usuario") in participant_user_ids}
    participation_percentage = (
        round(
            (
                len(evaluated_participants)
                / total_participants
            )
            * 100
        )
        if total_participants
        else 0
    )

    return {
        "participantes": total_participants,
        "encuestas": total_surveys,
        "participacion": participation_percentage,
        "nivel_predominante": predominant_risk,
        "riesgo_alto": high_count,

        "distribucion_riesgo": {
            "bajo": {
                "cantidad": low_count,
                "porcentaje": low_percentage,
            },
            "medio": {
                "cantidad": medium_count,
                "porcentaje": medium_percentage,
            },
            "alto": {
                "cantidad": high_count,
                "porcentaje": high_percentage,
            },
        },

        "habitos": {
            "reutiliza_contrasenas": percentage(
                reused_passwords
            ),
            "no_actualiza_contrasenas": percentage(
                passwords_not_updated
            ),
            "dificultad_phishing": percentage(
                phishing_difficulty
            ),
            "antivirus_desactualizado": percentage(
                outdated_antivirus
            ),
        },

        "evaluaciones_recientes": recent,
        "tendencia": _build_trend(surveys),
    }


def _build_trend(surveys: list[dict]) -> list[dict]:
    by_day = Counter(str(row.get("fecha_respuesta", ""))[:10] for row in surveys if row.get("fecha_respuesta"))
    return [{"fecha": day, "evaluaciones": by_day[day]} for day in sorted(by_day)]
