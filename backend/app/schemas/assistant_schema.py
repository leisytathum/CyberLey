from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssistantMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rol: Literal["usuario", "ciby"]
    texto: str = Field(min_length=1, max_length=500)


class AssistantQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    pregunta: str = Field(min_length=2, max_length=300)
    historial: list[AssistantMessage] = Field(default_factory=list, max_length=8)
