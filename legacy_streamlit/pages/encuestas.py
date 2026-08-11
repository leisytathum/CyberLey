import os
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from httpx import ConnectError, TimeoutException
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN
# =========================

st.set_page_config(
    page_title="CyberLey | Encuestas",
    page_icon="📝",
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

access_token = st.session_state.get("access_token")
refresh_token = st.session_state.get("refresh_token")

if access_token and refresh_token:

    sesion_restaurada = False

    for intento in range(2):
        try:
            supabase.auth.set_session(
                access_token,
                refresh_token
            )

            sesion_restaurada = True
            break

        except (TimeoutException, ConnectError):
            if intento == 0:
                time.sleep(1)

    if not sesion_restaurada:
        st.error(
            "No se pudo conectar con Supabase en este momento. "
            "Revisa tu conexión e intenta nuevamente."
        )

        if st.button("Reintentar conexión"):
            st.rerun()

        st.stop()


# =========================
# VALIDAR ADMIN
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
        index=2,
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

elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")

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
# FUNCIONES
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


def preparar_dataframe(
    respuestas: list[dict],
    participantes: list[dict]
) -> pd.DataFrame:

    df_respuestas = pd.DataFrame(
        respuestas
    )

    df_participantes = pd.DataFrame(
        participantes
    )

    if df_respuestas.empty:
        return df_respuestas

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
        df_respuestas["ciudad"] = "No disponible"
        df_respuestas["nivel_educativo"] = "No disponible"

    return df_respuestas


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
    <h1>Encuestas registradas</h1>
    <p>
        Consulta las evaluaciones completadas por los participantes,
        revisa sus respuestas y analiza sus resultados de riesgo digital.
    </p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# CONSULTAR DATOS
# =========================

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
            "id_usuario, nombre_completo, ciudad, nivel_educativo"
        )
    )

except Exception as error:
    st.error("No se pudieron consultar las encuestas.")
    st.write(error)
    st.stop()


df = preparar_dataframe(
    respuestas_ciberseguridad,
    participantes
)


# =========================
# SIN DATOS
# =========================

if df.empty:

    st.info(
        "Todavía no hay encuestas completadas. "
        "Cuando un usuario responda la evaluación nueva, aparecerá aquí."
    )

    st.stop()


# =========================
# MÉTRICAS
# =========================

total_encuestas = len(df)

riesgo_alto = len(
    df[
        df["clasificacion_riesgo"] == "alto"
    ]
)

riesgo_medio = len(
    df[
        df["clasificacion_riesgo"] == "medio"
    ]
)

riesgo_bajo = len(
    df[
        df["clasificacion_riesgo"] == "bajo"
    ]
)

promedio_puntaje = round(
    df["puntaje_riesgo"]
    .dropna()
    .mean(),
    1
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Encuestas completadas",
        total_encuestas
    )

with col2:
    st.metric(
        "Promedio de riesgo",
        promedio_puntaje
    )

with col3:
    st.metric(
        "Riesgo alto",
        riesgo_alto
    )

with col4:
    st.metric(
        "Riesgo bajo",
        riesgo_bajo
    )


# =========================
# FILTROS
# =========================

st.markdown(
    """
    <div class="section-title">
        Filtros de búsqueda
    </div>
    """,
    unsafe_allow_html=True
)

col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    filtro_riesgo = st.selectbox(
        "Clasificación de riesgo",
        [
            "Todas",
            "alto",
            "medio",
            "bajo"
        ]
    )

with col_filtro2:
    filtro_conocimiento = st.selectbox(
        "Nivel de conocimiento",
        [
            "Todos"
        ]
        + sorted(
            df["nivel_conocimiento"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with col_filtro3:
    filtro_phishing = st.selectbox(
        "Reconoce phishing",
        [
            "Todos"
        ]
        + sorted(
            df["reconoce_phishing"]
            .dropna()
            .unique()
            .tolist()
        )
    )


df_filtrado = df.copy()

if filtro_riesgo != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["clasificacion_riesgo"] == filtro_riesgo
    ]

if filtro_conocimiento != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["nivel_conocimiento"] == filtro_conocimiento
    ]

if filtro_phishing != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["reconoce_phishing"] == filtro_phishing
    ]


# =========================
# TABLA PRINCIPAL
# =========================

st.markdown(
    """
    <div class="section-title">
        Lista de encuestas completadas
    </div>
    """,
    unsafe_allow_html=True
)

columnas_tabla = [
    "fecha_respuesta",
    "nombre_completo",
    "ciudad",
    "nivel_educativo",
    "nivel_conocimiento",
    "reconoce_phishing",
    "estado_antivirus",
    "reutiliza_contrasenas",
    "puntaje_riesgo",
    "clasificacion_riesgo"
]

columnas_existentes = [
    columna
    for columna in columnas_tabla
    if columna in df_filtrado.columns
]

df_tabla = (
    df_filtrado[columnas_existentes]
    .sort_values(
        "fecha_respuesta",
        ascending=False
    )
)

df_tabla = df_tabla.rename(
    columns={
        "fecha_respuesta": "Fecha",
        "nombre_completo": "Participante",
        "ciudad": "Ciudad",
        "nivel_educativo": "Nivel educativo",
        "nivel_conocimiento": "Conocimiento",
        "reconoce_phishing": "Reconoce phishing",
        "estado_antivirus": "Antivirus",
        "reutiliza_contrasenas": "Reutiliza contraseñas",
        "puntaje_riesgo": "Puntaje",
        "clasificacion_riesgo": "Riesgo"
    }
)

st.dataframe(
    df_tabla,
    use_container_width=True,
    hide_index=True
)


# =========================
# DETALLE DE ENCUESTA
# =========================

st.markdown(
    """
    <div class="section-title">
        Detalle de una encuesta
    </div>
    """,
    unsafe_allow_html=True
)

opciones = []

for _, fila in df_filtrado.sort_values(
    "fecha_respuesta",
    ascending=False
).iterrows():

    nombre = fila.get(
        "nombre_completo",
        "Sin nombre"
    )

    fecha = str(
        fila.get(
            "fecha_respuesta",
            "Sin fecha"
        )
    )[:10]

    riesgo = fila.get(
        "clasificacion_riesgo",
        "sin clasificar"
    )

    id_respuesta = fila.get(
        "id_respuesta"
    )

    opciones.append(
        {
            "label": f"{nombre} | {fecha} | Riesgo: {riesgo}",
            "id_respuesta": id_respuesta
        }
    )


if not opciones:

    st.info(
        "No hay encuestas que coincidan con los filtros seleccionados."
    )

else:

    seleccion = st.selectbox(
        "Selecciona una encuesta para ver el detalle",
        opciones,
        format_func=lambda opcion: opcion["label"]
    )

    fila_detalle = df_filtrado[
        df_filtrado["id_respuesta"]
        == seleccion["id_respuesta"]
    ].iloc[0]

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Datos generales")

        st.write(
            "**Participante:**",
            fila_detalle.get(
                "nombre_completo",
                "No disponible"
            )
        )

        st.write(
            "**Ciudad:**",
            fila_detalle.get(
                "ciudad",
                "No disponible"
            )
        )

        st.write(
            "**Nivel educativo:**",
            fila_detalle.get(
                "nivel_educativo",
                "No disponible"
            )
        )

        st.write(
            "**Fecha de respuesta:**",
            str(
                fila_detalle.get(
                    "fecha_respuesta",
                    "No disponible"
                )
            )[:19]
        )

        st.write(
            "**Puntaje de riesgo:**",
            fila_detalle.get(
                "puntaje_riesgo",
                "No disponible"
            )
        )

        st.write(
            "**Clasificación:**",
            str(
                fila_detalle.get(
                    "clasificacion_riesgo",
                    "No disponible"
                )
            ).upper()
        )

    with col_b:
        st.markdown("### Respuestas principales")

        st.write(
            "**Usa nube:**",
            fila_detalle.get(
                "usa_nube",
                "No disponible"
            )
        )

        st.write(
            "**Plataforma de nube:**",
            fila_detalle.get(
                "plataforma_nube",
                "No disponible"
            )
        )

        st.write(
            "**Nivel de conocimiento:**",
            fila_detalle.get(
                "nivel_conocimiento",
                "No disponible"
            )
        )

        st.write(
            "**Reconoce phishing:**",
            fila_detalle.get(
                "reconoce_phishing",
                "No disponible"
            )
        )

        st.write(
            "**Estado del antivirus:**",
            fila_detalle.get(
                "estado_antivirus",
                "No disponible"
            )
        )

        st.write(
            "**Reutiliza contraseñas:**",
            fila_detalle.get(
                "reutiliza_contrasenas",
                "No disponible"
            )
        )

    st.markdown("### Observación")

    clasificacion = fila_detalle.get(
        "clasificacion_riesgo",
        "sin clasificar"
    )

    observacion = fila_detalle.get(
        "observacion",
        "Sin observación disponible."
    )

    if clasificacion == "alto":
        st.error(observacion)

    elif clasificacion == "medio":
        st.warning(observacion)

    elif clasificacion == "bajo":
        st.success(observacion)

    else:
        st.info(observacion)