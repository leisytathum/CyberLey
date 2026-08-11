from app.schemas.risk_schema import RiskInput


def calculate(payload: RiskInput) -> tuple[int, str, str]:
    score = 0
    score += {"Bajo": 20, "Medio": 10, "Alto": 0}.get(payload.nivel_conocimiento, 0)
    score += 15 if payload.manejo_ciberseguridad <= 2 else 8 if payload.manejo_ciberseguridad == 3 else 0
    score += {"Nunca": 12, "Rara vez": 8, "A veces": 4}.get(payload.frecuencia_info_seguridad, 0)
    score += {"No": 15, "A veces": 8}.get(payload.reconoce_phishing, 0)
    score += {"No": 10, "A veces": 5}.get(payload.identifica_herramientas_seguridad, 0)
    score += {
        "No tengo antivirus": 15,
        "Tengo antivirus, pero no está actualizado": 10,
        "No sé": 8,
    }.get(payload.estado_antivirus, 0)
    score += 8 if payload.estabilidad_conexion <= 2 else 4 if payload.estabilidad_conexion == 3 else 0
    score += {"Frecuentemente": 8, "A veces": 4}.get(payload.frecuencia_fallas_internet, 0)
    score += {"Nunca": 15, "Una vez al año": 8, "Cada 6 meses": 4}.get(payload.cambio_contrasenas_anual, 0)
    score += {"Sí": 15, "A veces": 8}.get(payload.reutiliza_contrasenas, 0)
    score += 8 if payload.importancia_actualizar_contrasenas <= 2 else 4 if payload.importancia_actualizar_contrasenas == 3 else 0

    if score >= 70:
        classification = "alto"
        observation = (
            "Presentas un nivel de riesgo alto. Es recomendable fortalecer tus "
            "prácticas de seguridad digital, actualizar contraseñas, evitar "
            "reutilizarlas y mejorar la identificación de amenazas como phishing."
        )
    elif score >= 35:
        classification = "medio"
        observation = (
            "Presentas un nivel de riesgo medio. Tienes algunas buenas prácticas, "
            "pero aún existen hábitos que pueden mejorar para reducir tu exposición "
            "a riesgos digitales."
        )
    else:
        classification = "bajo"
        observation = (
            "Presentas un nivel de riesgo bajo. Tus hábitos digitales son adecuados, "
            "aunque siempre es importante mantener buenas prácticas de ciberseguridad."
        )

    return score, classification, observation


def list_risk_responses(token: str, limit: int = 500) -> list[dict]:
    from app.database.supabase_client import SupabaseRESTClient

    return SupabaseRESTClient(token).get(
        "respuestas_encuesta_ciberseguridad",
        order="puntaje_riesgo.desc",
        limit=limit,
    )


def save_risk_response(token: str, user_id: str, payload: RiskInput) -> dict:
    from app.database.supabase_client import SupabaseRESTClient

    score, classification, observation = calculate(payload)
    row = {
        "id_usuario": user_id,
        **payload.model_dump(),
        "puntaje_riesgo": score,
        "clasificacion_riesgo": classification,
        "observacion": observation,
    }

    if row["usa_nube"] == "No":
        row["plataforma_nube"] = "No aplica"
        row["contenido_nube"] = "No aplica"

    data = SupabaseRESTClient(token).insert(
        "respuestas_encuesta_ciberseguridad",
        row,
    )

    return {
        "puntaje": score,
        "clasificacion": classification,
        "observacion": observation,
        "data": data,
    }
