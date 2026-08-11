from pydantic import BaseModel, Field


class RiskInput(BaseModel):
    usa_nube: str = "Sí"
    plataforma_nube: str = "Google Drive"
    contenido_nube: str = "Documentos personales"
    tipo_conexion: str = "Wi-Fi"
    nivel_conocimiento: str
    manejo_ciberseguridad: int = Field(ge=1, le=5)
    frecuencia_info_seguridad: str
    reconoce_phishing: str
    identifica_herramientas_seguridad: str
    estado_antivirus: str
    estabilidad_conexion: int = Field(ge=1, le=5)
    frecuencia_fallas_internet: str
    cambio_contrasenas_anual: str
    reutiliza_contrasenas: str
    importancia_actualizar_contrasenas: int = Field(ge=1, le=5)
