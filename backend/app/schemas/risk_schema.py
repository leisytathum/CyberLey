from typing import Literal
from pydantic import BaseModel, Field


class RiskInput(BaseModel):
    usa_nube: Literal["Sí", "No"] = "Sí"
    plataforma_nube: str = "Google Drive"
    contenido_nube: str = "Documentos personales"
    tipo_conexion: str = "Wi-Fi"
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
