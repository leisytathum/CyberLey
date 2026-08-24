from app.schemas.risk_schema import RiskInput
from app.services.risk_service import calculate


def make_payload(**changes) -> RiskInput:
    values = {
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
    values.update(changes)
    return RiskInput(**values)


def test_secure_habits_are_low_risk():
    score, classification, observation = calculate(make_payload())
    assert score == 0
    assert classification == "bajo"
    assert observation


def test_insecure_habits_are_high_risk():
    payload = make_payload(
        nivel_conocimiento="Bajo",
        manejo_ciberseguridad=1,
        frecuencia_info_seguridad="Nunca",
        reconoce_phishing="No",
        identifica_herramientas_seguridad="No",
        estado_antivirus="No tengo antivirus",
        estabilidad_conexion=1,
        frecuencia_fallas_internet="Frecuentemente",
        cambio_contrasenas_anual="Nunca",
        reutiliza_contrasenas="Sí",
        importancia_actualizar_contrasenas=1,
    )
    score, classification, _ = calculate(payload)
    assert score == 141
    assert classification == "alto"
