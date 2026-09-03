from pydantic import BaseModel, ConfigDict, Field


class AssistantQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    pregunta: str = Field(min_length=2, max_length=300)
