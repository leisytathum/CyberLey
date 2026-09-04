from unittest.mock import patch

from app.services.assistant_service import answer_user_question


def test_assistant_explains_first_step_without_database_access():
    result = answer_user_question("token", "user", "¿Qué debo hacer primero?")
    assert result["intent"] == "inicio"
    assert result["accion"]["path"] == "/usuario/encuesta"
    assert result["sugerencias"]


def test_assistant_recognizes_accents_and_security_topics():
    result = answer_user_question("token", "user", "¿Qué es el phishing?")
    assert result["intent"] == "phishing"
    assert "mensaje falso" in result["respuesta"]


def test_assistant_explains_how_to_sign_out():
    result = answer_user_question("token", "user", "¿Cómo puedo cerrar sesión?")
    assert result["intent"] == "sesion"
    assert "esquina superior derecha" in result["respuesta"]


def test_assistant_returns_safe_supported_topics_for_unknown_question():
    result = answer_user_question("token", "user", "Cuéntame algo completamente distinto")
    assert result["intent"] == "ayuda_general"
    assert "no logré entender" in result["respuesta"]
    assert result["sugerencias"]


def test_incident_question_is_not_confused_with_first_step():
    result = answer_user_question("token", "user", "¿Qué hago si abrí un enlace sospechoso?")
    assert result["intent"] == "incidente"
    assert "Cambia la contraseña" in result["respuesta"]


def test_assistant_tolerates_a_typo_in_an_open_question():
    result = answer_user_question("token", "user", "Holaa, en qué me puedes ayudar?")
    assert result["intent"] == "saludo"
    assert "Estoy aquí para ayudarte" in result["respuesta"]


def test_assistant_explains_its_capabilities():
    result = answer_user_question("token", "user", "¿Qué puedo preguntarte?")
    assert result["intent"] == "capacidades"
    assert "Puedo mostrarte" in result["respuesta"]


def test_urgent_account_incident_has_priority_over_password_advice():
    result = answer_user_question("token", "user", "Me hackearon y robaron mi contraseña, ¿qué hago?")
    assert result["intent"] == "incidente"
    assert "cierra las sesiones" in result["respuesta"]


def test_assistant_handles_public_wifi_question():
    result = answer_user_question("token", "user", "¿Puedo usar el wifi gratis del aeropuerto?")
    assert result["intent"] == "wifi_publico"
    assert "datos de tu teléfono" in result["respuesta"]


def test_assistant_handles_lost_device_question():
    result = answer_user_question("token", "user", "Me robaron mi celular")
    assert result["intent"] == "dispositivo_perdido"
    assert "bloquearlo" in result["respuesta"]


def test_assistant_handles_impersonation_question():
    result = answer_user_question("token", "user", "Se hacen pasar por mí en una cuenta falsa")
    assert result["intent"] == "suplantacion"
    assert "capturas" in result["respuesta"]


def test_assistant_limits_suggestions_to_three():
    result = answer_user_question("token", "user", "¿Qué puedes hacer?")
    assert len(result["sugerencias"]) <= 3


def test_assistant_answers_how_are_you_with_spelling_error():
    result = answer_user_question("token", "user", "como etas ciby")
    assert result["intent"] == "estado"
    assert "muy bien" in result["respuesta"]


def test_assistant_reacts_kindly_when_user_is_worried():
    result = answer_user_question("token", "user", "estoy preocupada y necesito ayuda")
    assert result["intent"] == "estado_usuario_preocupado"
    assert "paso a paso" in result["respuesta"]


def test_assistant_does_not_tell_user_to_use_own_words():
    questions = ["¿Qué puedes hacer?", "algo que no entiendes xyz"]
    for question in questions:
        result = answer_user_question("token", "user", question)
        assert "propias palabras" not in result["respuesta"]


def test_fallback_suggestion_buttons_are_understood_by_ciby():
    expected = {
        "Necesito usar CyberLey": "usar_cyberley",
        "Quiero cuidar mis cuentas": "proteger_cuentas",
        "Tuve un problema de seguridad": "tipo_problema",
    }
    for question, intent in expected.items():
        result = answer_user_question("token", "user", question)
        assert result["intent"] == intent
        assert result["intent"] != "ayuda_general"


def test_assistant_keeps_context_when_user_shared_password_after_link():
    history = [{"rol": "usuario", "texto": "Abrí un link raro"}, {"rol": "ciby", "texto": "¿Ingresaste información?"}]
    result = answer_user_question("token", "user", "sí puse mi contraseña", history)
    assert result["intent"] == "credencial_expuesta"
    assert "cambia esa contraseña" in result["respuesta"]


def test_assistant_keeps_context_when_user_only_names_the_message_channel():
    history = [{"rol": "usuario", "texto": "Me mandaron un link, ¿será real?"}, {"rol": "ciby", "texto": "¿Dónde te llegó?"}]
    result = answer_user_question("token", "user", "por whatsapp", history)
    assert result["intent"] == "canal_sospechoso"
    assert "aplicación oficial" in result["respuesta"]


def test_assistant_understands_follow_up_about_requested_login():
    history = [{"rol": "usuario", "texto": "Me llegó un correo raro"}, {"rol": "ciby", "texto": "¿Qué te pide hacer?"}]
    result = answer_user_question("token", "user", "iniciar sesión", history)
    assert result["intent"] == "phishing_inicio_sesion"
    assert "No inicies sesión desde el enlace" in result["respuesta"]


def test_assistant_remembers_more_than_one_user_message():
    history = [
        {"rol": "usuario", "texto": "Me mandaron un link raro"},
        {"rol": "ciby", "texto": "¿Dónde llegó?"},
        {"rol": "usuario", "texto": "Por WhatsApp"},
        {"rol": "ciby", "texto": "¿Qué te pide?"},
    ]
    result = answer_user_question("token", "user", "pide un código", history)
    assert result["intent"] == "solicitud_codigo"
    assert "No compartas" in result["respuesta"]


def test_assistant_asks_one_question_when_request_is_ambiguous():
    result = answer_user_question("token", "user", "¿esto es seguro?")
    assert result["intent"] == "pregunta_ambigua"
    assert result["respuesta"].count("?") == 1


def test_assistant_refuses_account_intrusion_and_offers_recovery():
    result = answer_user_question("token", "user", "cómo hackeo un facebook")
    assert result["intent"] == "solicitud_no_segura"
    assert "recuperar tu propia cuenta" in result["respuesta"]


def test_assistant_does_not_diagnose_malware_from_slow_internet():
    result = answer_user_question("token", "user", "mi internet está lento tengo virus?")
    assert result["intent"] == "diagnostico_incierto"
    assert result["respuesta"].startswith("No necesariamente")


def test_assistant_never_requests_or_repeats_a_shared_secret():
    result = answer_user_question("token", "user", "mi contraseña es SuperSecreta123")
    assert result["intent"] == "dato_sensible"
    assert "SuperSecreta123" not in result["respuesta"]
    assert "no necesito conocerlo" in result["respuesta"]


def test_password_quality_question_is_not_treated_as_shared_secret():
    result = answer_user_question("token", "user", "mi contraseña es segura?")
    assert result["intent"] == "evaluar_contrasena"
    assert "No me envíes la contraseña" in result["respuesta"]


def test_unexpected_verification_code_gets_specific_advice():
    result = answer_user_question("token", "user", "me llegó un código de instagram y yo no hice nada")
    assert result["intent"] == "codigo_inesperado"
    assert "No compartas ese código" in result["respuesta"]


@patch("app.services.assistant_knowledge.available_surveys")
def test_assistant_mentions_only_real_available_surveys(mock_surveys):
    mock_surveys.return_value = [
        {"id": "1", "titulo": "Hábitos reales", "respondida": False},
        {"id": "2", "titulo": "Ya completada", "respondida": True},
    ]
    result = answer_user_question("token", "user", "¿qué evaluaciones tengo?")
    assert result["intent"] == "evaluaciones_disponibles"
    assert "Hábitos reales" in result["respuesta"]
    assert "Ya completada" not in result["respuesta"]


@patch("app.services.assistant_knowledge.list_guides")
def test_assistant_mentions_only_guides_returned_by_cyberley(mock_guides):
    mock_guides.return_value = {"items": [{"id_guia": "1", "titulo": "Protege tu correo"}]}
    result = answer_user_question("token", "user", "¿qué guías hay?")
    assert result["intent"] == "guias_disponibles"
    assert "Protege tu correo" in result["respuesta"]
