from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.report_schema import ReportRequest
from app.schemas.risk_schema import RiskInput


def valid_risk_data():
    return {
        "nivel_conocimiento": "Alto",
        "manejo_ciberseguridad": 5,
        "frecuencia_info_seguridad": "Frecuentemente",
        "reconoce_phishing": "Sí",
        "identifica_herramientas_seguridad": "Sí",
        "estado_antivirus": "Tengo antivirus actualizado",
        "estabilidad_conexion": 5,
        "frecuencia_fallas_internet": "Nunca",
        "cambio_contrasenas_anual": "Cada 3 meses o menos",
        "reutiliza_contrasenas": "No",
        "importancia_actualizar_contrasenas": 5,
    }


def test_risk_payload_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        RiskInput(**valid_risk_data(), campo_inventado=True)


def test_cloud_fields_are_normalized_when_cloud_is_not_used():
    payload = RiskInput(**valid_risk_data(), usa_nube="No")
    assert payload.plataforma_nube == "No aplica"
    assert payload.contenido_nube == "No aplica"


def test_report_rejects_inverted_date_range():
    with pytest.raises(ValidationError):
        ReportRequest(fecha_desde=date(2026, 9, 2), fecha_hasta=date(2026, 1, 1))
