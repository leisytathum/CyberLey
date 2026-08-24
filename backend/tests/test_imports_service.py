import pandas as pd

from app.services.imports_service import clean_historic_csv, validate_csv_content


def historic_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [[
            "2026-01-01 GMT-6", "Si", None, None, "Medio", "3",
            "A veces", "Sí", "Sí", "Tengo antivirus actualizado",
            "Wifi", "4", "Nunca", "Cada 6 meses", "No", "5",
        ]],
        columns=[f"columna_{index}" for index in range(16)],
    )


def test_historic_csv_is_normalized():
    cleaned = clean_historic_csv(historic_frame())
    assert cleaned.loc[0, "usa_nube"] == "Sí"
    assert cleaned.loc[0, "tipo_conexion"] == "Wi-Fi"
    assert cleaned.loc[0, "plataforma_nube"] == "No aplica"
    assert cleaned.loc[0, "fecha_respuesta"] == "2026-01-01"


def test_csv_validation_returns_preview_and_download():
    result = validate_csv_content(
        "historico.csv",
        historic_frame().to_csv(index=False).encode("utf-8"),
    )
    assert result["filas"] == 1
    assert result["vista_limpia"][0]["tipo_conexion"] == "Wi-Fi"
    assert result["csv_base64"]
