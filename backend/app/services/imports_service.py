from io import BytesIO
import base64

import pandas as pd


def validate_csv_content(filename: str, content: bytes) -> dict:
    if not filename.lower().endswith(".csv"):
        raise ValueError("El archivo debe ser CSV.")

    try:
        try:
            original = pd.read_csv(BytesIO(content))
        except UnicodeDecodeError:
            original = pd.read_csv(BytesIO(content), encoding="latin-1")
    except Exception as exc:
        raise ValueError(f"No se pudo leer el CSV: {exc}") from exc
    cleaned = clean_historic_csv(original)
    csv_bytes = cleaned.to_csv(index=False).encode("utf-8-sig")
    return {
        "archivo": filename,
        "filas": len(original),
        "columnas_originales": len(original.columns),
        "columnas": list(cleaned.columns),
        "columnas_eliminadas": len(original.columns) - len(cleaned.columns),
        "nulos_originales": int(original.isna().sum().sum()),
        "nulos_limpios": int(cleaned.isna().sum().sum()),
        "vista_original": _records(original),
        "vista_limpia": _records(cleaned),
        "csv_base64": base64.b64encode(csv_bytes).decode("ascii"),
    }


def _records(frame: pd.DataFrame, limit: int = 100) -> list[dict]:
    sample = frame.head(limit).astype(object)
    return sample.where(pd.notna(sample), None).to_dict(orient="records")


def clean_historic_csv(original: pd.DataFrame) -> pd.DataFrame:
    frame = original.copy()
    frame = frame.drop(columns=[c for c in frame.columns if str(c).startswith("Unnamed:")], errors="ignore")
    if len(frame.columns) < 16:
        raise ValueError("El archivo debe contener al menos las 16 columnas de la encuesta histórica.")
    names = [
        "fecha_respuesta", "usa_nube", "plataforma_nube", "contenido_nube",
        "nivel_conocimiento", "manejo_ciberseguridad", "frecuencia_info_seguridad",
        "reconoce_phishing", "identifica_herramientas_seguridad", "estado_antivirus",
        "tipo_conexion", "estabilidad_conexion", "frecuencia_fallas_internet",
        "cambio_contrasenas_anual", "reutiliza_contrasenas", "importancia_actualizar_contrasenas",
    ]
    frame = frame.rename(columns={frame.columns[i]: name for i, name in enumerate(names)})
    for column in frame.select_dtypes(include="object").columns:
        frame[column] = frame[column].map(lambda value: " ".join(str(value).strip().split()) if pd.notna(value) else value)
    frame["plataforma_nube"] = frame["plataforma_nube"].fillna("No aplica")
    frame["contenido_nube"] = frame["contenido_nube"].fillna("No aplica")
    frame["tipo_conexion"] = frame["tipo_conexion"].replace({"Rauter": "Router", "Wifi": "Wi-Fi", "Wi Fi": "Wi-Fi"})
    frame["usa_nube"] = frame["usa_nube"].replace({"Si": "Sí", "SI": "Sí"})
    for column in ("manejo_ciberseguridad", "estabilidad_conexion", "importancia_actualizar_contrasenas"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["fecha_respuesta"] = frame["fecha_respuesta"].astype(str).str.replace(" GMT-6", "", regex=False)
    return frame
