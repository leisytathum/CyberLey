from app.schemas.risk_schema import RiskInput
from concurrent.futures import ThreadPoolExecutor


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


def list_risk_responses(token: str) -> list[dict]:
    from app.database.supabase_client import SupabaseRESTClient

    db = SupabaseRESTClient(token)
    with ThreadPoolExecutor(max_workers=5) as executor:
        rows_future = executor.submit(
            db.get_all,
            "respuestas_encuesta_ciberseguridad",
            order="puntaje_riesgo.desc",
        )
        participants_future = executor.submit(db.get_all, "participantes")
        profiles_future = executor.submit(db.get_all, "perfiles")
        dynamic_future = executor.submit(
            db.get_all,
            "aplicaciones_encuesta",
            order="fecha_respuesta.desc",
        )
        definitions_future = executor.submit(db.get_all, "encuestas_dinamicas")
        rows = rows_future.result()
        participants = {
            x.get("id_usuario"): x for x in participants_future.result()
        }
        profiles = {x.get("id"): x for x in profiles_future.result()}
        dynamic_rows = dynamic_future.result()
        definitions = {x.get("id"): x for x in definitions_future.result()}
    legacy = [
        {
            **row,
            "tipo_evaluacion": "Evaluación general",
            "nombre_usuario": participants.get(row.get("id_usuario"), {}).get("nombre_completo")
            or profiles.get(row.get("id_usuario"), {}).get("nombre_completo")
            or "Usuario desconocido",
        }
        for row in rows
        if profiles.get(row.get("id_usuario"), {}).get("rol") == "usuario"
    ]
    dynamic = [
        {
            **row,
            "id_respuesta": row.get("id"),
            "tipo_evaluacion": definitions.get(row.get("id_encuesta"), {}).get("titulo") or "Encuesta configurable",
            "puntaje_riesgo": float(row.get("porcentaje_riesgo") or 0),
            "nombre_usuario": participants.get(row.get("id_usuario"), {}).get("nombre_completo")
            or profiles.get(row.get("id_usuario"), {}).get("nombre_completo")
            or "Usuario desconocido",
        }
        for row in dynamic_rows
        if profiles.get(row.get("id_usuario"), {}).get("rol") == "usuario"
    ]
    return sorted(legacy + dynamic, key=lambda row: str(row.get("fecha_respuesta") or ""), reverse=True)


def risk_analytics(token: str) -> dict:
    rows = list_risk_responses(token)
    total = len(rows)
    scores = [x.get("puntaje_riesgo") for x in rows if isinstance(x.get("puntaje_riesgo"), (int, float))]
    distribution = {level: sum(x.get("clasificacion_riesgo") == level for x in rows) for level in ("bajo", "medio", "alto")}
    factors = {
        "Reutiliza contraseñas": sum(x.get("reutiliza_contrasenas") in {"Sí", "A veces"} for x in rows),
        "No reconoce phishing": sum(x.get("reconoce_phishing") in {"No", "A veces"} for x in rows),
        "Antivirus desactualizado o ausente": sum(x.get("estado_antivirus") in {"No tengo antivirus", "Tengo antivirus, pero no está actualizado", "No sé"} for x in rows),
        "Bajo conocimiento": sum(x.get("nivel_conocimiento") == "Bajo" for x in rows),
        "Nunca cambia contraseñas": sum(x.get("cambio_contrasenas_anual") == "Nunca" for x in rows),
        "Poca información de seguridad": sum(x.get("frecuencia_info_seguridad") in {"Nunca", "Rara vez"} for x in rows),
        "Manejo bajo de ciberseguridad": sum(x.get("manejo_ciberseguridad") in {1, 2} for x in rows),
        "Conexión inestable": sum(x.get("estabilidad_conexion") in {1, 2} for x in rows),
    }
    trend: dict[str, int] = {}
    for row in rows:
        day = str(row.get("fecha_respuesta") or "")[:10]
        if day: trend[day] = trend.get(day, 0) + 1
    def cross(field: str) -> list[dict]:
        values: dict[tuple[str, str], int] = {}
        for row in rows:
            key = (str(row.get(field) or "Sin dato"), str(row.get("clasificacion_riesgo") or "sin clasificar"))
            values[key] = values.get(key, 0) + 1
        return [{"categoria": a, "riesgo": b, "cantidad": value} for (a, b), value in values.items()]
    return {
        "items": rows, "total": total,
        "promedio_riesgo": round(sum(scores) / len(scores), 1) if scores else 0,
        "distribucion": distribution,
        "factores": [{"nombre": name, "cantidad": value} for name, value in sorted(factors.items(), key=lambda x: x[1], reverse=True)],
        "tendencia": [{"fecha": day, "evaluaciones": trend[day]} for day in sorted(trend)],
        "conocimiento_riesgo": cross("nivel_conocimiento"),
        "phishing_riesgo": cross("reconoce_phishing"),
    }


def user_risk_responses(token: str, user_id: str) -> list[dict]:
    from app.database.supabase_client import SupabaseRESTClient

    db = SupabaseRESTClient(token)
    legacy = db.get_all(
        "respuestas_encuesta_ciberseguridad",
        filters={"id_usuario": f"eq.{user_id}"},
        order="fecha_respuesta.desc",
    )
    dynamic = db.get_all(
        "aplicaciones_encuesta",
        filters={"id_usuario": f"eq.{user_id}"},
        order="fecha_respuesta.desc",
    )
    normalized_dynamic = [
        {
            **row,
            "id_respuesta": row.get("id"),
            "puntaje_riesgo": float(row.get("porcentaje_riesgo") or 0),
            "tipo_evaluacion": "Encuesta configurable",
        }
        for row in dynamic
    ]
    return sorted(legacy + normalized_dynamic, key=lambda row: str(row.get("fecha_respuesta") or ""), reverse=True)


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
