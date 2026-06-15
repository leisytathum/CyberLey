import os
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from httpx import ConnectError, TimeoutException
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Análisis de riesgo",
    page_icon="⚠️",
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
# RESTAURAR SESIÓN
# =========================

def restaurar_sesion():
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    if not access_token or not refresh_token:
        return

    for intento in range(2):
        try:
            supabase.auth.set_session(
                access_token,
                refresh_token
            )
            return

        except (TimeoutException, ConnectError):
            if intento == 0:
                time.sleep(1)

    st.error(
        "No se pudo conectar con Supabase en este momento. "
        "Revisa tu conexión e intenta nuevamente."
    )

    if st.button("Reintentar conexión"):
        st.rerun()

    st.stop()


restaurar_sesion()


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
# CONSULTAS A SUPABASE
# =========================

def consultar_tabla(
    nombre_tabla: str,
    columnas: str = "*"
) -> list[dict]:

    respuesta = (
        supabase
        .table(nombre_tabla)
        .select(columnas)
        .execute()
    )

    return respuesta.data or []


try:
    respuestas_ciberseguridad = consultar_tabla(
        "respuestas_encuesta_ciberseguridad",
        (
            "id_respuesta, id_usuario, fecha_respuesta, usa_nube, "
            "plataforma_nube, contenido_nube, nivel_conocimiento, "
            "manejo_ciberseguridad, frecuencia_info_seguridad, "
            "reconoce_phishing, identifica_herramientas_seguridad, "
            "estado_antivirus, tipo_conexion, estabilidad_conexion, "
            "frecuencia_fallas_internet, cambio_contrasenas_anual, "
            "reutiliza_contrasenas, importancia_actualizar_contrasenas, "
            "puntaje_riesgo, clasificacion_riesgo, observacion"
        )
    )

    participantes = consultar_tabla(
        "participantes",
        (
            "id_usuario, nombre_completo, edad, genero, "
            "ciudad, nivel_educativo"
        )
    )

except Exception as error:
    st.error("No se pudieron cargar los datos de riesgo.")
    st.write(error)
    st.stop()


# =========================
# SIDEBAR
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
        index=3,
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

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")

elif menu == "📥 Importar datos históricos":
    st.switch_page("pages/importar_datos.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "📄 Reportes":
    st.switch_page("pages/reportes.py")

elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Análisis de riesgo digital</h1>
<p>
Consulta la distribución de niveles de riesgo, identifica hábitos inseguros
y analiza los resultados obtenidos en la encuesta de ciberseguridad.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# PREPARAR DATAFRAMES
# =========================

df_respuestas = pd.DataFrame(
    respuestas_ciberseguridad
)

df_participantes = pd.DataFrame(
    participantes
)

if df_respuestas.empty:
    st.info(
        "Todavía no existen respuestas registradas en la nueva encuesta "
        "de ciberseguridad."
    )
    st.stop()


df_respuestas["fecha_respuesta"] = pd.to_datetime(
    df_respuestas["fecha_respuesta"],
    errors="coerce"
)

df_respuestas["puntaje_riesgo"] = pd.to_numeric(
    df_respuestas["puntaje_riesgo"],
    errors="coerce"
)

df_respuestas["clasificacion_riesgo"] = (
    df_respuestas["clasificacion_riesgo"]
    .fillna("sin clasificar")
    .str.lower()
)


if not df_participantes.empty:
    df_respuestas = df_respuestas.merge(
        df_participantes,
        on="id_usuario",
        how="left"
    )

else:
    df_respuestas["nombre_completo"] = "No disponible"


# =========================
# MÉTRICAS PRINCIPALES
# =========================

total_evaluaciones = len(df_respuestas)

promedio_riesgo = round(
    df_respuestas["puntaje_riesgo"]
    .dropna()
    .mean(),
    1
)

cantidad_alto = len(
    df_respuestas[
        df_respuestas["clasificacion_riesgo"] == "alto"
    ]
)

cantidad_medio = len(
    df_respuestas[
        df_respuestas["clasificacion_riesgo"] == "medio"
    ]
)

cantidad_bajo = len(
    df_respuestas[
        df_respuestas["clasificacion_riesgo"] == "bajo"
    ]
)

porcentaje_alto = round(
    cantidad_alto / total_evaluaciones * 100,
    1
)

porcentaje_medio = round(
    cantidad_medio / total_evaluaciones * 100,
    1
)

porcentaje_bajo = round(
    cantidad_bajo / total_evaluaciones * 100,
    1
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Evaluaciones",
        total_evaluaciones
    )

with col2:
    st.metric(
        "Promedio de riesgo",
        promedio_riesgo
    )

with col3:
    st.metric(
        "Riesgo alto",
        f"{porcentaje_alto}%"
    )

with col4:
    st.metric(
        "Riesgo medio",
        f"{porcentaje_medio}%"
    )


# =========================
# PESTAÑAS
# =========================

tab_general, tab_factores, tab_detalle = st.tabs(
    [
        "📊 Vista general",
        "⚠️ Factores de riesgo",
        "📋 Detalle de evaluaciones"
    ]
)


# =========================
# TAB 1: VISTA GENERAL
# =========================

with tab_general:

    col_a, col_b = st.columns(
        [1, 1]
    )

    with col_a:

        st.markdown(
            """
            <div class="section-title">
                Distribución por clasificación de riesgo
            </div>
            """,
            unsafe_allow_html=True
        )

        df_clasificacion = pd.DataFrame({
            "Clasificación": [
                "Alto",
                "Medio",
                "Bajo"
            ],
            "Cantidad": [
                cantidad_alto,
                cantidad_medio,
                cantidad_bajo
            ]
        })

        st.bar_chart(
            df_clasificacion,
            x="Clasificación",
            y="Cantidad",
            use_container_width=True
        )

    with col_b:

        st.markdown(
            """
            <div class="section-title">
                Tendencia de evaluaciones
            </div>
            """,
            unsafe_allow_html=True
        )

        tendencia = (
            df_respuestas
            .dropna(
                subset=["fecha_respuesta"]
            )
            .assign(
                fecha=lambda datos: (
                    datos["fecha_respuesta"]
                    .dt.date
                )
            )
            .groupby("fecha")
            .size()
            .reset_index(name="Evaluaciones")
        )

        st.line_chart(
            tendencia,
            x="fecha",
            y="Evaluaciones",
            use_container_width=True
        )

    st.markdown(
        """
        <div class="section-title">
            Puntajes de riesgo registrados
        </div>
        """,
        unsafe_allow_html=True
    )

    df_puntajes = (
        df_respuestas[
            [
                "fecha_respuesta",
                "puntaje_riesgo",
                "clasificacion_riesgo"
            ]
        ]
        .dropna(
            subset=["puntaje_riesgo"]
        )
        .sort_values(
            "fecha_respuesta"
        )
    )

    st.bar_chart(
        df_puntajes,
        x="fecha_respuesta",
        y="puntaje_riesgo",
        use_container_width=True
    )


# =========================
# TAB 2: FACTORES DE RIESGO
# =========================

with tab_factores:

    st.markdown(
        """
        <div class="section-title">
            Hábitos y condiciones que aumentan el riesgo
        </div>
        """,
        unsafe_allow_html=True
    )

    factores = {
        "Reutiliza contraseñas": int(
            df_respuestas[
                df_respuestas["reutiliza_contrasenas"].isin(
                    [
                        "Sí",
                        "A veces"
                    ]
                )
            ].shape[0]
        ),

        "No reconoce phishing": int(
            df_respuestas[
                df_respuestas["reconoce_phishing"].isin(
                    [
                        "No",
                        "A veces"
                    ]
                )
            ].shape[0]
        ),

        "Antivirus desactualizado o ausente": int(
            df_respuestas[
                df_respuestas["estado_antivirus"].isin(
                    [
                        "No tengo antivirus",
                        "Tengo antivirus, pero no está actualizado",
                        "No sé"
                    ]
                )
            ].shape[0]
        ),

        "Bajo conocimiento": int(
            df_respuestas[
                df_respuestas["nivel_conocimiento"] == "Bajo"
            ].shape[0]
        ),

        "Nunca cambia contraseñas": int(
            df_respuestas[
                df_respuestas["cambio_contrasenas_anual"] == "Nunca"
            ].shape[0]
        ),

        "Poca información de seguridad": int(
            df_respuestas[
                df_respuestas["frecuencia_info_seguridad"].isin(
                    [
                        "Nunca",
                        "Rara vez"
                    ]
                )
            ].shape[0]
        ),

        "Manejo bajo de ciberseguridad": int(
            df_respuestas[
                df_respuestas["manejo_ciberseguridad"].isin(
                    [
                        1,
                        2
                    ]
                )
            ].shape[0]
        ),

        "Conexión inestable": int(
            df_respuestas[
                df_respuestas["estabilidad_conexion"].isin(
                    [
                        1,
                        2
                    ]
                )
            ].shape[0]
        )
    }

    df_factores = (
        pd.DataFrame(
            list(factores.items()),
            columns=[
                "Factor de riesgo",
                "Cantidad"
            ]
        )
        .sort_values(
            "Cantidad",
            ascending=False
        )
    )

    st.bar_chart(
        df_factores,
        x="Factor de riesgo",
        y="Cantidad",
        use_container_width=True
    )

    st.markdown(
        """
        <div class="section-title">
            Relación entre conocimiento y clasificación de riesgo
        </div>
        """,
        unsafe_allow_html=True
    )

    tabla_conocimiento = pd.crosstab(
        df_respuestas["nivel_conocimiento"],
        df_respuestas["clasificacion_riesgo"]
    )

    st.dataframe(
        tabla_conocimiento,
        use_container_width=True
    )

    st.markdown(
        """
        <div class="section-title">
            Relación entre phishing y clasificación de riesgo
        </div>
        """,
        unsafe_allow_html=True
    )

    tabla_phishing = pd.crosstab(
        df_respuestas["reconoce_phishing"],
        df_respuestas["clasificacion_riesgo"]
    )

    st.dataframe(
        tabla_phishing,
        use_container_width=True
    )


# =========================
# TAB 3: DETALLE
# =========================

with tab_detalle:

    st.markdown(
        """
        <div class="section-title">
            Evaluaciones registradas
        </div>
        """,
        unsafe_allow_html=True
    )

    filtro_riesgo = st.selectbox(
        "Filtrar por clasificación",
        [
            "Todas",
            "alto",
            "medio",
            "bajo"
        ]
    )

    df_detalle = df_respuestas.copy()

    if filtro_riesgo != "Todas":
        df_detalle = df_detalle[
            df_detalle["clasificacion_riesgo"] == filtro_riesgo
        ]

    columnas_detalle = [
        "fecha_respuesta",
        "nombre_completo",
        "nivel_conocimiento",
        "reconoce_phishing",
        "estado_antivirus",
        "cambio_contrasenas_anual",
        "reutiliza_contrasenas",
        "puntaje_riesgo",
        "clasificacion_riesgo",
        "observacion"
    ]

    columnas_existentes = [
        columna
        for columna in columnas_detalle
        if columna in df_detalle.columns
    ]

    df_detalle = (
        df_detalle[columnas_existentes]
        .sort_values(
            "fecha_respuesta",
            ascending=False
        )
    )

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True
    )