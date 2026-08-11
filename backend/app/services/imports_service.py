from io import BytesIO

import pandas as pd


def validate_csv_content(filename: str, content: bytes) -> dict:
    if not filename.lower().endswith(".csv"):
        raise ValueError("El archivo debe ser CSV.")

    try:
        dataframe = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise ValueError(f"No se pudo leer el CSV: {exc}") from exc

    return {
        "archivo": filename,
        "filas": len(dataframe),
        "columnas": list(dataframe.columns),
    }
