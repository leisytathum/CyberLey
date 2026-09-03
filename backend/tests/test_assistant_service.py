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
