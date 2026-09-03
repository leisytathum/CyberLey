from typing import Literal
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    tipo: Literal[
        "Reporte general",
        "Participantes registrados",
        "Resultados de riesgo",
        "Respuestas de encuestas",
        "Hábitos digitales",
    ] = "Reporte general"
    ciudad: str | None = Field(default=None, max_length=120)
    nivel_educativo: str | None = Field(default=None, max_length=120)
    riesgo: Literal["bajo", "medio", "alto"] | None = None
    fecha_desde: date | None = None
    fecha_hasta: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")
        return self
