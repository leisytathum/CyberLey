import os
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Importar datos históricos",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

if not SUPABASE_KEY:
    st.error("No se encontró SUPABASE_KEY en el archivo .env.")
    st.stop()

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================
# VALIDAR ACCESO ADMIN
# =========================

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

if st.session_state.get("rol") != "admin":
    st.warning("Esta sección es exclusiva para administradores.")
    st.switch_page("pages/usuario.py")


# =========================
# CARGAR CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "dashboard.css"

    with open(
        ruta_css,
        "r",
        encoding="utf-8"
    ) as archivo:

        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()


# =========================
# SIDEBAR ADMIN
# =========================

with st.sidebar:

    st.image(
        str(ROOT_DIR / "Logo.png"),
        use_container_width=True
    )

    st.markdown(
        "<div class='sidebar-title'>Panel Administrador</div>",
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Menú",
        [
            "🏠 Inicio",
            "👥 Participantes",
            "📝 Encuestas",
            "⚠️ Riesgo",
            "🧹 Limpieza de datos",
            "📥 Importar datos históricos",
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=5,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "🚪 Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.clear()
        st.switch_page("app.py")


# =========================
# NAVEGACIÓN
# =========================

if menu == "🏠 Inicio":
    st.switch_page("pages/dashboard.py")

elif menu == "👥 Participantes":
    st.switch_page("pages/participantes.py")

elif menu == "📝 Encuestas":
    st.switch_page("pages/encuestas.py")

elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "📄 Reportes":
    st.switch_page("pages/reportes.py")

elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")


# =========================
# FUNCIONES DE LIMPIEZA
# =========================

def limpiar_texto(valor):
    """
    Elimina espacios adicionales.
    """

    if pd.isna(valor):
        return valor

    return " ".join(
        str(valor).strip().split()
    )


def limpiar_csv(
    df_original: pd.DataFrame
) -> pd.DataFrame:
    """
    Limpia y normaliza el CSV histórico.
    """

    df = df_original.copy()

    # -------------------------
    # ELIMINAR COLUMNAS VACÍAS
    # -------------------------

    columnas_unnamed = [
        columna
        for columna in df.columns
        if str(columna).startswith("Unnamed:")
    ]

    df = df.drop(
        columns=columnas_unnamed,
        errors="ignore"
    )

    # -------------------------
    # RENOMBRAR COLUMNAS
    # -------------------------

    nombres_nuevos = {
        df.columns[0]: "fecha_respuesta",
        df.columns[1]: "usa_nube",
        df.columns[2]: "plataforma_nube",
        df.columns[3]: "contenido_nube",
        df.columns[4]: "nivel_conocimiento",
        df.columns[5]: "manejo_ciberseguridad",
        df.columns[6]: "frecuencia_info_seguridad",
        df.columns[7]: "reconoce_phishing",
        df.columns[8]: "identifica_herramientas_seguridad",
        df.columns[9]: "estado_antivirus",
        df.columns[10]: "tipo_conexion",
        df.columns[11]: "estabilidad_conexion",
        df.columns[12]: "frecuencia_fallas_internet",
        df.columns[13]: "cambio_contrasenas_anual",
        df.columns[14]: "reutiliza_contrasenas",
        df.columns[15]: "importancia_actualizar_contrasenas"
    }

    df = df.rename(
        columns=nombres_nuevos
    )

    # -------------------------
    # LIMPIAR TEXTOS
    # -------------------------

    columnas_texto = df.select_dtypes(
        include="object"
    ).columns

    for columna in columnas_texto:
        df[columna] = (
            df[columna]
            .apply(limpiar_texto)
        )

    # -------------------------
    # NORMALIZAR NULOS VÁLIDOS
    # -------------------------

    df["plataforma_nube"] = (
        df["plataforma_nube"]
        .fillna("No aplica")
    )

    df["contenido_nube"] = (
        df["contenido_nube"]
        .fillna("No aplica")
    )

    df["importancia_actualizar_contrasenas"] = (
        df["importancia_actualizar_contrasenas"]
        .fillna("Sin respuesta")
    )

    # -------------------------
    # NORMALIZAR CONEXIONES
    # -------------------------

    equivalencias_conexion = {
        "Rauter": "Router",
        "Wifi": "Wi-Fi",
        "ADSL": "ADSL",
        (
            "Satelital "
            "(Línea de Abonado Digital Asimétrica)"
        ): "Satelital"
    }

    df["tipo_conexion"] = (
        df["tipo_conexion"]
        .replace(
            equivalencias_conexion
        )
    )

    # -------------------------
    # NORMALIZAR RESPUESTAS
    # -------------------------

    equivalencias_si_no = {
        "Sí": "Sí",
        "Si": "Sí",
        "No": "No"
    }

    df["usa_nube"] = (
        df["usa_nube"]
        .replace(
            equivalencias_si_no
        )
    )

    # -------------------------
    # CONVERTIR ESCALAS
    # -------------------------

    columnas_numericas = [
        "manejo_ciberseguridad",
        "estabilidad_conexion"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    df[
        "importancia_actualizar_contrasenas"
    ] = pd.to_numeric(
        df[
            "importancia_actualizar_contrasenas"
        ],
        errors="coerce"
    )

    # -------------------------
    # FECHA
    # -------------------------

    df["fecha_respuesta"] = (
        df["fecha_respuesta"]
        .astype(str)
        .str.replace(
            " GMT-6",
            "",
            regex=False
        )
    )

    return df


def convertir_csv(
    dataframe: pd.DataFrame
) -> bytes:

    return dataframe.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Importar datos históricos</h1>
<p>
Carga una encuesta externa en formato CSV, revisa su calidad
y genera una versión limpia para el análisis estadístico.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# INFORMACIÓN
# =========================

st.info(
    "Este módulo no modifica las encuestas registradas dentro de "
    "CyberLey ni altera las tablas actuales de Supabase."
)


# =========================
# CARGAR ARCHIVO
# =========================

archivo_csv = st.file_uploader(
    "Selecciona el archivo CSV de la encuesta histórica",
    type=["csv"]
)


if archivo_csv is None:

    st.markdown("### Instrucciones")

    st.write(
        "Sube el archivo exportado desde Google Forms. "
        "Después podrás revisar los datos originales, "
        "visualizar la limpieza y descargar una copia corregida."
    )

    st.stop()


# =========================
# LEER CSV
# =========================

try:
    df_original = pd.read_csv(
        archivo_csv
    )

except UnicodeDecodeError:
    df_original = pd.read_csv(
        archivo_csv,
        encoding="latin-1"
    )

except Exception as error:
    st.error(
        "No se pudo leer el archivo CSV."
    )

    st.write(error)

    st.stop()


# =========================
# LIMPIAR CSV
# =========================

try:
    df_limpio = limpiar_csv(
        df_original
    )

except Exception as error:
    st.error(
        "El archivo no tiene la estructura esperada."
    )

    st.write(error)

    st.stop()


# =========================
# MÉTRICAS
# =========================

columnas_eliminadas = (
    len(df_original.columns)
    - len(df_limpio.columns)
)

valores_nulos_originales = int(
    df_original
    .isna()
    .sum()
    .sum()
)

valores_nulos_limpios = int(
    df_limpio
    .isna()
    .sum()
    .sum()
)


col1, col2, col3, col4 = st.columns(
    4
)

with col1:
    st.metric(
        "Filas cargadas",
        len(df_original)
    )

with col2:
    st.metric(
        "Columnas originales",
        len(df_original.columns)
    )

with col3:
    st.metric(
        "Columnas eliminadas",
        columnas_eliminadas
    )

with col4:
    st.metric(
        "Nulos después de limpieza",
        valores_nulos_limpios
    )


# =========================
# PESTAÑAS
# =========================

tab_original, tab_limpio, tab_resumen = (
    st.tabs(
        [
            "📄 Datos originales",
            "🧹 Datos limpios",
            "📊 Resumen"
        ]
    )
)


# =========================
# TAB ORIGINAL
# =========================

with tab_original:

    st.markdown(
        "### Vista previa del archivo original"
    )

    st.caption(
        f"Valores vacíos detectados: "
        f"{valores_nulos_originales}"
    )

    st.dataframe(
        df_original,
        use_container_width=True,
        hide_index=True
    )


# =========================
# TAB LIMPIO
# =========================

with tab_limpio:

    st.markdown(
        "### Vista previa del archivo limpio"
    )

    st.caption(
        f"Valores vacíos después de limpieza: "
        f"{valores_nulos_limpios}"
    )

    st.dataframe(
        df_limpio,
        use_container_width=True,
        hide_index=True
    )


# =========================
# TAB RESUMEN
# =========================

with tab_resumen:

    st.markdown(
        "### Resumen de la transformación"
    )

    st.write(
        f"✅ Se procesaron {len(df_limpio)} respuestas."
    )

    st.write(
        f"✅ Se eliminaron {columnas_eliminadas} columnas innecesarias."
    )

    st.write(
        "✅ Los vacíos relacionados con personas que no utilizan "
        "almacenamiento en la nube fueron reemplazados por "
        "'No aplica'."
    )

    st.write(
        "✅ Se normalizaron variantes como 'Rauter' y 'Wifi'."
    )

    st.write(
        "✅ El CSV limpio quedó listo para utilizarse en Jupyter."
    )


# =========================
# DESCARGAR ARCHIVO LIMPIO
# =========================

st.write("")

st.download_button(
    label="⬇️ Descargar CSV limpio",
    data=convertir_csv(
        df_limpio
    ),
    file_name=(
        "encuesta_ciberseguridad_limpia.csv"
    ),
    mime="text/csv",
    use_container_width=True
)