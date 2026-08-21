from __future__ import annotations

from app.database.supabase_client import (
    SupabaseRESTClient,
)


def list_surveys(
    token: str,
    limit: int = 500,
) -> list[dict]:
    client = SupabaseRESTClient(token)

    surveys = client.get(
        "respuestas_encuesta_ciberseguridad",
        order="fecha_respuesta.desc",
        limit=limit,
    )

    profiles = client.get(
        "perfiles",
        limit=limit,
    )

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

        result.append(
            {
                **survey,
                "nombre_usuario": profile.get(
                    "nombre_completo",
                    "Usuario desconocido",
                ),
                "rol_usuario": profile.get(
                    "rol",
                    "usuario",
                ),
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