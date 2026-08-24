from typing import Literal

from pydantic import BaseModel


class ReportRequest(BaseModel):
    tipo: Literal[
        "Reporte general",
        "Participantes registrados",
        "Resultados de riesgo",
        "Respuestas de encuestas",
        "Hábitos digitales",
    ] = "Reporte general"
    ciudad: str | None = None
    nivel_educativo: str | None = None
    riesgo: Literal["bajo", "medio", "alto"] | None = None
    fecha_desde: str | None = None
    fecha_hasta: str | None = None
