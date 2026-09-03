import base64
import csv
from datetime import datetime
from io import StringIO

from app.database.supabase_client import SupabaseRESTClient
from app.schemas.report_schema import ReportRequest


def list_reports(token: str, limit: int = 500) -> list[dict]:
    return SupabaseRESTClient(token).get_all("reportes", order="fecha_generacion.desc")


REPORT_COLUMNS = {
    "Participantes registrados": ["nombre_completo", "edad", "genero", "ciudad", "nivel_educativo", "fecha_registro"],
    "Resultados de riesgo": ["nombre_completo", "ciudad", "nivel_educativo", "fecha_respuesta", "puntaje_riesgo", "clasificacion_riesgo", "observacion"],
    "Respuestas de encuestas": ["nombre_completo", "ciudad", "nivel_educativo", "fecha_respuesta", "usa_nube", "plataforma_nube", "contenido_nube", "nivel_conocimiento", "manejo_ciberseguridad", "frecuencia_info_seguridad", "reconoce_phishing", "identifica_herramientas_seguridad", "estado_antivirus", "tipo_conexion", "estabilidad_conexion", "frecuencia_fallas_internet", "cambio_contrasenas_anual", "reutiliza_contrasenas", "importancia_actualizar_contrasenas"],
    "Hábitos digitales": ["nombre_completo", "nivel_conocimiento", "reconoce_phishing", "estado_antivirus", "cambio_contrasenas_anual", "reutiliza_contrasenas", "frecuencia_info_seguridad", "tipo_conexion", "puntaje_riesgo", "clasificacion_riesgo"],
}
GENERAL_COLUMNS = ["nombre_completo", "edad", "genero", "ciudad", "nivel_educativo", "fecha_registro", "fecha_respuesta", "usa_nube", "nivel_conocimiento", "reconoce_phishing", "estado_antivirus", "reutiliza_contrasenas", "puntaje_riesgo", "clasificacion_riesgo", "observacion"]
COLUMN_LABELS = {
    "nombre_completo": "Participante", "edad": "Edad", "genero": "Género",
    "ciudad": "Ciudad", "nivel_educativo": "Nivel educativo",
    "fecha_registro": "Fecha de registro", "fecha_respuesta": "Fecha de respuesta",
    "usa_nube": "Usa nube", "plataforma_nube": "Plataforma de nube",
    "contenido_nube": "Contenido en nube", "nivel_conocimiento": "Nivel de conocimiento",
    "manejo_ciberseguridad": "Manejo de ciberseguridad",
    "frecuencia_info_seguridad": "Frecuencia de información de seguridad",
    "reconoce_phishing": "Reconoce phishing",
    "identifica_herramientas_seguridad": "Identifica herramientas de seguridad",
    "estado_antivirus": "Estado del antivirus", "tipo_conexion": "Tipo de conexión",
    "estabilidad_conexion": "Estabilidad de conexión",
    "frecuencia_fallas_internet": "Frecuencia de fallas de internet",
    "cambio_contrasenas_anual": "Cambio de contraseñas anual",
    "reutiliza_contrasenas": "Reutiliza contraseñas",
    "importancia_actualizar_contrasenas": "Importancia de actualizar contraseñas",
    "puntaje_riesgo": "Puntaje de riesgo",
    "clasificacion_riesgo": "Clasificación de riesgo", "observacion": "Observación",
}


def generate_report(token: str, user_id: str, request: ReportRequest) -> dict:
    db = SupabaseRESTClient(token)
    profiles = {x.get("id"): x for x in db.get_all("perfiles")}
    participants = [x for x in db.get_all("participantes") if profiles.get(x.get("id_usuario"), {}).get("rol") == "usuario"]
    surveys_by_user: dict[str, list[dict]] = {}
    for row in db.get_all("respuestas_encuesta_ciberseguridad"):
        surveys_by_user.setdefault(row.get("id_usuario"), []).append(row)
    rows = []
    for participant in participants:
        surveys = surveys_by_user.get(participant.get("id_usuario")) or [{}]
        rows.extend([{**participant, **survey} for survey in surveys])
    date_from = request.fecha_desde.isoformat() if request.fecha_desde else None
    date_to = request.fecha_hasta.isoformat() if request.fecha_hasta else None
    def keep(row: dict) -> bool:
        date = str(row.get("fecha_respuesta") or "")[:10]
        return (
            (not request.ciudad or row.get("ciudad") == request.ciudad)
            and (not request.nivel_educativo or row.get("nivel_educativo") == request.nivel_educativo)
            and (not request.riesgo or row.get("clasificacion_riesgo") == request.riesgo)
            and (not date_from or not date or date >= date_from)
            and (not date_to or not date or date <= date_to)
        )
    rows = [row for row in rows if keep(row)]
    columns = REPORT_COLUMNS.get(request.tipo, GENERAL_COLUMNS)
    labels = [COLUMN_LABELS.get(column, column) for column in columns]
    preview = [
        {COLUMN_LABELS.get(column, column): row.get(column) for column in columns}
        for row in rows
    ]
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=labels)
    writer.writeheader(); writer.writerows(preview)
    description = f"Ciudad: {request.ciudad or 'Todas'}; Nivel educativo: {request.nivel_educativo or 'Todos'}; Riesgo: {request.riesgo or 'Todos'}; Filas exportadas: {len(preview)}"
    if preview:
        db.insert("reportes", {"generado_por": user_id, "tipo_reporte": request.tipo, "descripcion": description})
    filename = request.tipo.lower().replace(" ", "_") + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    return {"filas": len(preview), "vista_previa": preview[:100], "archivo": filename, "csv_base64": base64.b64encode(stream.getvalue().encode("utf-8-sig")).decode("ascii")}
