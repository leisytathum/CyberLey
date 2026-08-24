from app.database.supabase_client import SupabaseRESTClient


def _text(value) -> str:
    return " ".join(str(value or "").strip().split()).title()


def _participant_changes(rows: list[dict]) -> list[dict]:
    changes = []
    maps = {
        "genero": {"Prefiero No Responder": "Prefiero no responder"},
        "nivel_educativo": {"Tecnico": "Técnico"},
    }
    for row in rows:
        update = {}
        for field in ("nombre_completo", "ciudad", "genero", "nivel_educativo"):
            cleaned = maps.get(field, {}).get(_text(row.get(field)), _text(row.get(field)))
            if cleaned and cleaned != row.get(field): update[field] = cleaned
        if update:
            changes.append({"id": row.get("id_participante"), "actual": row, "cambios": update})
    return changes


def _survey_changes(rows: list[dict]) -> list[dict]:
    changes = []
    yes_no = {"Si": "Sí", "si": "Sí", "SI": "Sí"}
    connections = {"Wifi": "Wi-Fi", "Wi Fi": "Wi-Fi", "Rauter": "Router", "Adsl": "ADSL"}
    for row in rows:
        update = {}
        for field in ("usa_nube", "reutiliza_contrasenas"):
            cleaned = yes_no.get(str(row.get(field) or "").strip(), row.get(field))
            if cleaned != row.get(field): update[field] = cleaned
        connection = connections.get(_text(row.get("tipo_conexion")), _text(row.get("tipo_conexion")))
        if connection and connection != row.get("tipo_conexion"): update["tipo_conexion"] = connection
        if (update.get("usa_nube", row.get("usa_nube"))) == "No":
            if not row.get("plataforma_nube"): update["plataforma_nube"] = "No aplica"
            if not row.get("contenido_nube"): update["contenido_nube"] = "No aplica"
        if update: changes.append({"id": row.get("id_respuesta"), "actual": row, "cambios": update})
    return changes


def get_diagnostic(token: str) -> dict:
    db = SupabaseRESTClient(token)
    profiles = {x.get("id"): x for x in db.get_all("perfiles")}
    participants = [x for x in db.get_all("participantes") if profiles.get(x.get("id_usuario"), {}).get("rol") == "usuario"]
    surveys = db.get_all("respuestas_encuesta_ciberseguridad")
    participant_changes = _participant_changes(participants)
    survey_changes = _survey_changes(surveys)
    duplicate_keys = {}
    for row in participants:
        key = (_text(row.get("nombre_completo")), row.get("edad"), _text(row.get("ciudad")))
        duplicate_keys.setdefault(key, []).append(row)
    duplicates = [row for group in duplicate_keys.values() if len(group) > 1 for row in group]
    required = ("id_usuario", "usa_nube", "nivel_conocimiento", "manejo_ciberseguridad", "reconoce_phishing", "estado_antivirus", "tipo_conexion", "reutiliza_contrasenas", "puntaje_riesgo", "clasificacion_riesgo")
    incomplete = [row for row in surveys if any(row.get(field) is None or row.get(field) == "" for field in required)]
    evaluated = {row.get("id_usuario") for row in surveys}
    without_survey = [row for row in participants if row.get("id_usuario") not in evaluated]
    missing_by_column = {field: sum(row.get(field) is None or row.get(field) == "" for row in surveys) for field in (surveys[0].keys() if surveys else [])}
    return {
        "resumen": {"participantes": len(participants), "encuestas": len(surveys), "correcciones": len(participant_changes) + len(survey_changes), "duplicados": len(duplicates), "incompletas": len(incomplete), "sin_encuesta": len(without_survey)},
        "cambios_participantes": participant_changes,
        "cambios_encuestas": survey_changes,
        "duplicados": duplicates,
        "encuestas_incompletas": incomplete,
        "usuarios_sin_encuesta": without_survey,
        "faltantes_por_columna": missing_by_column,
    }


def apply_cleaning(token: str, target: str) -> dict:
    diagnostic = get_diagnostic(token)
    db = SupabaseRESTClient(token)
    key = "cambios_participantes" if target == "participantes" else "cambios_encuestas"
    table = "participantes" if target == "participantes" else "respuestas_encuesta_ciberseguridad"
    id_field = "id_participante" if target == "participantes" else "id_respuesta"
    updated = 0
    for item in diagnostic[key]:
        if item["cambios"]:
            db.update(table, item["cambios"], filters={id_field: f"eq.{item['id']}"})
            updated += 1
    return {"actualizados": updated, "objetivo": target}
