from pydantic import BaseModel


class CSVValidationResponse(BaseModel):
    archivo: str
    filas: int
    columnas: list[str]
