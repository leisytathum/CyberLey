from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SurveyOption(StrictSchema):
    etiqueta: str = Field(min_length=1, max_length=160)
    puntos: int = Field(default=0, ge=0, le=100)

class SurveyQuestion(StrictSchema):
    texto: str = Field(min_length=3, max_length=500)
    tipo: Literal["opcion", "escala", "si_no", "texto"]
    requerida: bool = True
    opciones: list[SurveyOption] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_options(self):
        if self.tipo == "opcion" and len(self.opciones) < 2:
            raise ValueError("Una pregunta de opción necesita al menos dos respuestas.")
        if self.tipo == "si_no" and not self.opciones:
            self.opciones = [SurveyOption(etiqueta="Sí", puntos=0), SurveyOption(etiqueta="No", puntos=0)]
        if self.tipo == "escala" and not self.opciones:
            self.opciones = [SurveyOption(etiqueta=str(value), puntos=value - 1) for value in range(1, 6)]
        if self.tipo == "texto" and self.opciones:
            raise ValueError("Una pregunta de texto no puede incluir opciones.")
        labels = [option.etiqueta.casefold() for option in self.opciones]
        if len(labels) != len(set(labels)):
            raise ValueError("Las opciones de una pregunta no pueden repetirse.")
        return self


class SurveyCreate(StrictSchema):
    titulo: str = Field(min_length=3, max_length=180)
    descripcion: str = Field(default="", max_length=500)
    preguntas: list[SurveyQuestion] = Field(min_length=1, max_length=100)

    @field_validator("preguntas")
    @classmethod
    def unique_questions(cls, questions: list[SurveyQuestion]):
        texts = [question.texto.casefold() for question in questions]
        if len(texts) != len(set(texts)):
            raise ValueError("La encuesta no puede contener preguntas repetidas.")
        return questions


class SurveyState(StrictSchema):
    estado: Literal["borrador", "publicada", "cerrada"]


class SurveyAnswer(StrictSchema):
    id_pregunta: UUID
    valor: Any


class SurveySubmission(StrictSchema):
    respuestas: list[SurveyAnswer] = Field(min_length=1, max_length=100)

    @field_validator("respuestas")
    @classmethod
    def unique_answers(cls, answers: list[SurveyAnswer]):
        question_ids = [answer.id_pregunta for answer in answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Cada pregunta debe responderse una sola vez.")
        return answers
