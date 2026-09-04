from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GuideCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    titulo: str = Field(min_length=3, max_length=180)
    categoria: str = Field(min_length=2, max_length=80)
    descripcion: str = Field(default="", max_length=1000)
    contenido: str = Field(default="", max_length=50000)
    nivel_recomendado: Literal["bajo", "medio", "alto", "general"] = "general"
    tipo_recurso: Literal["documento", "pdf", "imagen", "video", "interactivo"] = "documento"
    estado: Literal["borrador", "publicada"] = "borrador"


class GuideAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    participantes: list[UUID] = Field(min_length=1, max_length=1000)
    mensaje: str = Field(default="", max_length=1000)


class GuideUpdate(GuideCreate):
    pass
