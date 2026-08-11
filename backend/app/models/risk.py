from typing import Literal, TypedDict


class RiskResult(TypedDict):
    puntaje: int
    clasificacion: Literal["bajo", "medio", "alto"]
    observacion: str
