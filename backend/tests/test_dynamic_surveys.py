from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.dynamic_survey_schema import (
    SurveyAnswer,
    SurveyCreate,
    SurveyOption,
    SurveyQuestion,
    SurveySubmission,
)
from app.services.dynamic_surveys_service import _validated_value
from app.utils.exceptions import BusinessValidationError


def test_rejects_duplicate_option_labels():
    with pytest.raises(ValidationError):
        SurveyQuestion(
            texto="¿Reconoces mensajes sospechosos?",
            tipo="opcion",
            opciones=[
                SurveyOption(etiqueta="Sí", puntos=0),
                SurveyOption(etiqueta="sí", puntos=10),
            ],
        )


def test_rejects_duplicate_questions():
    question = SurveyQuestion(
        texto="¿Actualizas tus contraseñas?",
        tipo="si_no",
    )
    with pytest.raises(ValidationError):
        SurveyCreate(titulo="Hábitos seguros", preguntas=[question, question])


def test_rejects_duplicate_answers():
    question_id = uuid4()
    with pytest.raises(ValidationError):
        SurveySubmission(
            respuestas=[
                SurveyAnswer(id_pregunta=question_id, valor="Sí"),
                SurveyAnswer(id_pregunta=question_id, valor="No"),
            ]
        )


def test_rejects_option_not_defined_by_question():
    question = {
        "texto": "¿Usas autenticación de dos pasos?",
        "tipo": "opcion",
        "opciones": [{"etiqueta": "Sí", "puntos": 0}, {"etiqueta": "No", "puntos": 10}],
    }
    with pytest.raises(BusinessValidationError):
        _validated_value(question, "Tal vez")


def test_trims_text_answers_and_limits_length():
    question = {"texto": "Comentario", "tipo": "texto", "requerida": True}
    assert _validated_value(question, "  respuesta segura  ") == "respuesta segura"
    with pytest.raises(BusinessValidationError):
        _validated_value(question, "x" * 2001)
