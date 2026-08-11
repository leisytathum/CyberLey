from typing import TypedDict


class SurveyResponse(TypedDict, total=False):
    id: str
    id_usuario: str
    puntaje_riesgo: int
    clasificacion_riesgo: str
    observacion: str
