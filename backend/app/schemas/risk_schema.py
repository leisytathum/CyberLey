from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    usa_nube: Literal["Sí", "No"] = "Sí"
    plataforma_nube: str = Field(default="Google Drive", min_length=1, max_length=100)
    contenido_nube: str = Field(default="Documentos personales", min_length=1, max_length=200)
    tipo_conexion: str = Field(default="Wi-Fi", min_length=1, max_length=80)
    nivel_conocimiento: Literal["Bajo", "Medio", "Alto"]
    manejo_ciberseguridad: int = Field(ge=1, le=5)
    frecuencia_info_seguridad: Literal["Nunca", "Rara vez", "A veces", "Frecuentemente"]
    reconoce_phishing: Literal["Sí", "No", "A veces"]
    identifica_herramientas_seguridad: Literal["Sí", "No", "A veces"]
    estado_antivirus: Literal["Tengo antivirus actualizado", "Tengo antivirus, pero no está actualizado", "No tengo antivirus", "No sé"]
    estabilidad_conexion: int = Field(ge=1, le=5)
    frecuencia_fallas_internet: Literal["Nunca", "Rara vez", "A veces", "Frecuentemente"]
    cambio_contrasenas_anual: Literal["Nunca", "Una vez al año", "Cada 6 meses", "Cada 3 meses o menos"]
    reutiliza_contrasenas: Literal["Sí", "No", "A veces"]
    importancia_actualizar_contrasenas: int = Field(ge=1, le=5)

    @model_validator(mode="after")
    def normalize_cloud_fields(self):
        if self.usa_nube == "No":
            self.plataforma_nube = "No aplica"
            self.contenido_nube = "No aplica"
        return self
