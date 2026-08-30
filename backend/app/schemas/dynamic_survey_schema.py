from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

class SurveyOption(BaseModel):
    etiqueta: str = Field(min_length=1, max_length=160)
    puntos: int = Field(default=0, ge=0, le=100)

class SurveyQuestion(BaseModel):
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
        return self

class SurveyCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=180)
    descripcion: str = Field(default="", max_length=1200)
    preguntas: list[SurveyQuestion] = Field(min_length=1, max_length=100)

class SurveyState(BaseModel):
    estado: Literal["borrador", "publicada", "cerrada"]

class SurveyAnswer(BaseModel):
    id_pregunta: str
    valor: Any

class SurveySubmission(BaseModel):
    respuestas: list[SurveyAnswer] = Field(min_length=1)
