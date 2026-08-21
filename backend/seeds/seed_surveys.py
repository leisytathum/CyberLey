from __future__ import annotations

import httpx

from app.config.settings import settings


TEST_SURVEYS = [
    {
        "email": "usuario1@cyberley.com",
        "participante": {
            "nombre_completo": "Ana Martínez",
            "edad": 22,
            "genero": "Femenino",
            "ciudad": "La Ceiba",
            "nivel_educativo": "Universitario",
        },
        "respuestas": {
            "usa_misma_contrasena": False,
            "usa_wifi_publico": False,
            "reconoce_phishing": "si",
            "usa_doble_factor": True,
            "tiene_antivirus": True,
            "actualiza_contrasenas": True,
            "comparte_info_redes": False,
            "nivel_conocimiento": "alto",
        },
        "resultado": {
            "puntaje_riesgo": 1,
            "clasificacion_riesgo": "bajo",
            "observacion": (
                "El usuario presenta buenas prácticas "
                "generales de ciberseguridad."
            ),
        },
    },
    {
        "email": "usuario2@cyberley.com",
        "participante": {
            "nombre_completo": "Carlos López",
            "edad": 29,
            "genero": "Masculino",
            "ciudad": "La Ceiba",
            "nivel_educativo": "Secundaria",
        },
        "respuestas": {
            "usa_misma_contrasena": True,
            "usa_wifi_publico": True,
            "reconoce_phishing": "a_veces",
            "usa_doble_factor": True,
            "tiene_antivirus": True,
            "actualiza_contrasenas": False,
            "comparte_info_redes": False,
            "nivel_conocimiento": "medio",
        },
        "resultado": {
            "puntaje_riesgo": 5,
            "clasificacion_riesgo": "medio",
            "observacion": (
                "El usuario presenta algunas prácticas "
                "que pueden aumentar su exposición digital."
            ),
        },
    },
    {
        "email": "usuario3@cyberley.com",
        "participante": {
            "nombre_completo": "María Hernández",
            "edad": 35,
            "genero": "Femenino",
            "ciudad": "La Ceiba",
            "nivel_educativo": "Universitario",
        },
        "respuestas": {
            "usa_misma_contrasena": True,
            "usa_wifi_publico": True,
            "reconoce_phishing": "no",
            "usa_doble_factor": False,
            "tiene_antivirus": False,
            "actualiza_contrasenas": False,
            "comparte_info_redes": True,
            "nivel_conocimiento": "bajo",
        },
        "resultado": {
            "puntaje_riesgo": 10,
            "clasificacion_riesgo": "alto",
            "observacion": (
                "El usuario presenta múltiples prácticas "
                "de riesgo y requiere recomendaciones."
            ),
        },
    },
]


def _headers() -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _get_existing_participant(
    client: httpx.Client,
    user_id: str,
) -> dict | None:
    response = client.get(
        f"{settings.supabase_url}/rest/v1/participantes",
        headers=_headers(),
        params={
            "select": "*",
            "id_usuario": f"eq.{user_id}",
            "limit": "1",
        },
    )

    response.raise_for_status()

    rows = response.json()

    return rows[0] if rows else None


def _create_participant(
    client: httpx.Client,
    user_id: str,
    data: dict,
) -> dict:
    existing = _get_existing_participant(
        client,
        user_id,
    )

    if existing:
        print(
            f"  ↳ Participante existente: "
            f"{data['nombre_completo']}"
        )
        return existing

    headers = {
        **_headers(),
        "Prefer": "return=representation",
    }

    response = client.post(
        f"{settings.supabase_url}/rest/v1/participantes",
        headers=headers,
        json={
            "id_usuario": user_id,
            **data,
        },
    )

    response.raise_for_status()

    participant = response.json()[0]

    print(
        f"  ✓ Participante creado: "
        f"{data['nombre_completo']}"
    )

    return participant


def _get_existing_survey(
    client: httpx.Client,
    participant_id: str,
) -> dict | None:
    response = client.get(
        f"{settings.supabase_url}/rest/v1/encuestas",
        headers=_headers(),
        params={
            "select": "*",
            "id_participante": f"eq.{participant_id}",
            "limit": "1",
        },
    )

    response.raise_for_status()

    rows = response.json()

    return rows[0] if rows else None


def _create_survey(
    client: httpx.Client,
    participant_id: str,
) -> tuple[dict, bool]:
    existing = _get_existing_survey(
        client,
        participant_id,
    )

    if existing:
        print("  ↳ Encuesta existente.")
        return existing, False

    headers = {
        **_headers(),
        "Prefer": "return=representation",
    }

    response = client.post(
        f"{settings.supabase_url}/rest/v1/encuestas",
        headers=headers,
        json={
            "id_participante": participant_id,
            "estado": "completada",
        },
    )

    response.raise_for_status()

    survey = response.json()[0]

    print("  ✓ Encuesta creada.")

    return survey, True


def _create_answers(
    client: httpx.Client,
    survey_id: str,
    answers: dict,
) -> None:
    headers = {
        **_headers(),
        "Prefer": "return=representation",
    }

    response = client.post(
        f"{settings.supabase_url}/rest/v1/respuestas_encuesta",
        headers=headers,
        json={
            "id_encuesta": survey_id,
            **answers,
        },
    )

    response.raise_for_status()

    print("  ✓ Respuestas creadas.")


def _create_risk_result(
    client: httpx.Client,
    survey_id: str,
    result: dict,
) -> None:
    headers = {
        **_headers(),
        "Prefer": "return=representation",
    }

    response = client.post(
        f"{settings.supabase_url}/rest/v1/resultados_riesgo",
        headers=headers,
        json={
            "id_encuesta": survey_id,
            **result,
        },
    )

    response.raise_for_status()

    print(
        f"  ✓ Riesgo: "
        f"{result['clasificacion_riesgo']}"
    )


def seed_surveys(
    users: dict[str, str],
) -> None:
    print("\n=== DATOS DE ENCUESTAS ===")

    with httpx.Client(timeout=30) as client:
        for test_data in TEST_SURVEYS:
            email = test_data["email"]

            user_id = users.get(email)

            if not user_id:
                print(
                    f"  ! No se encontró el usuario {email}. "
                    f"Se omite."
                )
                continue

            print(f"\nProcesando {email}")

            participant = _create_participant(
                client,
                user_id,
                test_data["participante"],
            )

            survey, was_created = _create_survey(
                client,
                participant["id_participante"],
            )

            # Evita duplicar respuestas si se vuelve
            # a ejecutar el seed.
            if not was_created:
                print(
                    "  ↳ Ya tenía una encuesta. "
                    "No se duplicarán respuestas."
                )
                continue

            _create_answers(
                client,
                survey["id_encuesta"],
                test_data["respuestas"],
            )

            _create_risk_result(
                client,
                survey["id_encuesta"],
                test_data["resultado"],
            )