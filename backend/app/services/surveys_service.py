from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from app.database.supabase_client import (
    SupabaseRESTClient,
)


def list_surveys(
    token: str,
    limit: int = 500,
) -> list[dict]:
    client = SupabaseRESTClient(token)

    with ThreadPoolExecutor(max_workers=3) as executor:
        surveys_future = executor.submit(
            client.get_all,
            "respuestas_encuesta_ciberseguridad",
            order="fecha_respuesta.desc",
        )
        profiles_future = executor.submit(client.get_all, "perfiles")
        participants_future = executor.submit(client.get_all, "participantes")
        surveys = surveys_future.result()
        profiles = profiles_future.result()
        participant_rows = participants_future.result()

    participants_by_user = {
        row.get("id_usuario"): row for row in participant_rows
    }

    profiles_by_id = {
        profile["id"]: profile
        for profile in profiles
    }

    result = []

    for survey in surveys:
        profile = profiles_by_id.get(
            survey.get("id_usuario"),
            {},
        )
        if profile.get("rol") != "usuario":
            continue
        participant = participants_by_user.get(survey.get("id_usuario"), {})

        result.append(
            {
                **survey,
                "nombre_usuario": participant.get("nombre_completo") or profile.get("nombre_completo") or "Usuario desconocido",
                "rol_usuario": profile.get(
                    "rol",
                    "usuario",
                ),
                "ciudad": participant.get("ciudad"),
                "nivel_educativo": participant.get("nivel_educativo"),
            }
        )

    return result


def get_survey_statistics(
    token: str,
) -> dict:
    surveys = list_surveys(token)

    total = len(surveys)

    low = sum(
        1
        for survey in surveys
        if survey.get(
            "clasificacion_riesgo"
        )
        == "bajo"
    )

    medium = sum(
        1
        for survey in surveys
        if survey.get(
            "clasificacion_riesgo"
        )
        == "medio"
    )

    high = sum(
        1
        for survey in surveys
        if survey.get(
            "clasificacion_riesgo"
        )
        == "alto"
    )

    scores = [
        survey.get("puntaje_riesgo")
        for survey in surveys
        if isinstance(
            survey.get("puntaje_riesgo"),
            (int, float),
        )
    ]

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores
        else 0
    )

    return {
        "total": total,
        "riesgo_bajo": low,
        "riesgo_medio": medium,
        "riesgo_alto": high,
        "promedio_riesgo": average_score,
    }
