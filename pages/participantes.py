import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Participantes",
    page_icon="👥",
    layout="wide"
)

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

if not SUPABASE_KEY:
    st.error("No se encontró SUPABASE_KEY en el archivo .env.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
access_token = st.session_state.get("access_token")
refresh_token = st.session_state.get("refresh_token")

if access_token and refresh_token:
    supabase.auth.set_session(
        access_token,
        refresh_token
    )

# =========================
# CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "dashboard.css"

    with open(ruta_css, "r", encoding="utf-8") as archivo:
        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()


# =========================
# VALIDAR SESIÓN
# =========================

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")


# =========================
# CONSULTAS A SUPABASE
# =========================

def consultar_tabla(nombre_tabla: str, columnas: str = "*") -> list[dict]:
    respuesta = (
        supabase
        .table(nombre_tabla)
        .select(columnas)
        .execute()
    )

    return respuesta.data or []


def preparar_datos_participantes() -> pd.DataFrame:
    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, nombre_completo, edad, genero, "
            "ciudad, nivel_educativo, fecha_registro"
        )
    )

    if not participantes:
        return pd.DataFrame()

    df_participantes = pd.DataFrame(participantes)

    # =========================
    # CANTIDAD DE ENCUESTAS
    # =========================

    encuestas = consultar_tabla(
        "encuestas",
        "id_encuesta, id_participante, fecha_aplicacion"
    )

    if encuestas:
        df_encuestas = pd.DataFrame(encuestas)

        cantidad_encuestas = (
            df_encuestas
            .groupby("id_participante")
            .size()
            .reset_index(name="encuestas_realizadas")
        )

        df_participantes = df_participantes.merge(
            cantidad_encuestas,
            on="id_participante",
            how="left"
        )

    else:
        df_encuestas = pd.DataFrame()
        df_participantes["encuestas_realizadas"] = 0

    # =========================
    # ÚLTIMO RESULTADO DE RIESGO
    # =========================

    resultados = consultar_tabla(
        "resultados_riesgo",
        (
            "id_encuesta, puntaje_riesgo, "
            "clasificacion_riesgo, fecha_calculo"
        )
    )

    if resultados and not df_encuestas.empty:
        df_resultados = pd.DataFrame(resultados)

        riesgo_por_participante = df_encuestas.merge(
            df_resultados,
            on="id_encuesta",
            how="inner"
        )

        riesgo_por_participante["fecha_calculo"] = pd.to_datetime(
            riesgo_por_participante["fecha_calculo"],
            errors="coerce"
        )

        ultimo_riesgo = (
            riesgo_por_participante
            .sort_values("fecha_calculo")
            .drop_duplicates(
                subset=["id_participante"],
                keep="last"
            )
            [
                [
                    "id_participante",
                    "puntaje_riesgo",
                    "clasificacion_riesgo"
                ]
            ]
        )

        df_participantes = df_participantes.merge(
            ultimo_riesgo,
            on="id_participante",
            how="left"
        )

    else:
        df_participantes["puntaje_riesgo"] = None
        df_participantes["clasificacion_riesgo"] = "Sin evaluar"

    # =========================
    # PROGRESO DE GUÍAS
    # =========================

    guias = consultar_tabla(
        "guias_ciberseguridad",
        "id_guia"
    )

    total_guias = len(guias)

    guias_completadas = consultar_tabla(
        "guias_completadas",
        "id_participante, id_guia"
    )

    if guias_completadas:
        df_guias = pd.DataFrame(guias_completadas)

        progreso = (
            df_guias
            .groupby("id_participante")["id_guia"]
            .nunique()
            .reset_index(name="guias_completadas")
        )

        df_participantes = df_participantes.merge(
            progreso,
            on="id_participante",
            how="left"
        )

    else:
        df_participantes["guias_completadas"] = 0

    df_participantes["guias_completadas"] = (
        df_participantes["guias_completadas"]
        .fillna(0)
        .astype(int)
    )

    if total_guias > 0:
        df_participantes["progreso_guias"] = (
            df_participantes["guias_completadas"]
            / total_guias
            * 100
        ).round(0).astype(int)

    else:
        df_participantes["progreso_guias"] = 0

    # =========================
    # RECOMENDACIONES PENDIENTES
    # =========================

    recomendaciones = consultar_tabla(
        "recomendaciones",
        "id_participante, estado"
    )

    if recomendaciones:
        df_recomendaciones = pd.DataFrame(recomendaciones)

        pendientes = (
            df_recomendaciones[
                df_recomendaciones["estado"] == "pendiente"
            ]
            .groupby("id_participante")
            .size()
            .reset_index(name="recomendaciones_pendientes")
        )

        df_participantes = df_participantes.merge(
            pendientes,
            on="id_participante",
            how="left"
        )

    else:
        df_participantes["recomendaciones_pendientes"] = 0

    # =========================
    # LIMPIEZA FINAL
    # =========================

    df_participantes["encuestas_realizadas"] = (
        df_participantes["encuestas_realizadas"]
        .fillna(0)
        .astype(int)
    )

    df_participantes["clasificacion_riesgo"] = (
        df_participantes["clasificacion_riesgo"]
        .fillna("Sin evaluar")
        .str.title()
    )

    df_participantes["recomendaciones_pendientes"] = (
        df_participantes["recomendaciones_pendientes"]
        .fillna(0)
        .astype(int)
    )

    return df_participantes


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
            "📊 Limpieza de datos",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=1,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")


if menu == "🏠 Inicio":
    st.switch_page("pages/dashboard.py")


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
    <div class="page-heading">
        <div>
            <h1>Participantes</h1>
            <p>
                Consulta los usuarios registrados, analiza sus resultados
                y revisa su progreso.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# CARGAR DATOS
# =========================

try:
    df = preparar_datos_participantes()

except Exception as error:
    st.error(f"No se pudieron cargar los participantes: {error}")
    st.stop()


if df.empty:
    st.info("Todavía no hay participantes registrados.")
    st.stop()


# =========================
# MÉTRICAS
# =========================

total_participantes = len(df)

participantes_evaluados = len(
    df[df["clasificacion_riesgo"] != "Sin Evaluar"]
)

riesgo_alto = len(
    df[df["clasificacion_riesgo"] == "Alto"]
)

promedio_progreso = round(
    df["progreso_guias"].mean(),
    1
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Participantes registrados",
        total_participantes
    )

with col2:
    st.metric(
        "Participantes evaluados",
        participantes_evaluados
    )

with col3:
    st.metric(
        "Riesgo alto",
        riesgo_alto
    )

with col4:
    st.metric(
        "Progreso promedio",
        f"{promedio_progreso}%"
    )


st.write("")


# =========================
# FILTROS
# =========================

st.markdown("### Buscar y filtrar")

filtro1, filtro2, filtro3, filtro4 = st.columns(4)

with filtro1:
    buscar_nombre = st.text_input(
        "Buscar por nombre",
        placeholder="Ejemplo: Ana Martínez"
    )

with filtro2:
    ciudades = ["Todas"] + sorted(
        df["ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad_seleccionada = st.selectbox(
        "Ciudad",
        ciudades
    )

with filtro3:
    niveles = ["Todos"] + sorted(
        df["nivel_educativo"]
        .dropna()
        .unique()
        .tolist()
    )

    nivel_seleccionado = st.selectbox(
        "Nivel educativo",
        niveles
    )

with filtro4:
    riesgos = [
        "Todos",
        "Sin Evaluar",
        "Bajo",
        "Medio",
        "Alto"
    ]

    riesgo_seleccionado = st.selectbox(
        "Nivel de riesgo",
        riesgos
    )


df_filtrado = df.copy()

if buscar_nombre:
    df_filtrado = df_filtrado[
        df_filtrado["nombre_completo"]
        .str.contains(
            buscar_nombre,
            case=False,
            na=False
        )
    ]

if ciudad_seleccionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["ciudad"] == ciudad_seleccionada
    ]

if nivel_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["nivel_educativo"] == nivel_seleccionado
    ]

if riesgo_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["clasificacion_riesgo"]
        == riesgo_seleccionado
    ]


# =========================
# TABLA
# =========================

st.caption(
    f"Mostrando {len(df_filtrado)} de {len(df)} participantes."
)

columnas_tabla = [
    "nombre_completo",
    "edad",
    "ciudad",
    "nivel_educativo",
    "encuestas_realizadas",
    "clasificacion_riesgo",
    "progreso_guias",
    "recomendaciones_pendientes"
]

st.dataframe(
    df_filtrado[columnas_tabla],
    use_container_width=True,
    hide_index=True,
    column_config={
        "nombre_completo": "Nombre completo",
        "edad": "Edad",
        "ciudad": "Ciudad",
        "nivel_educativo": "Nivel educativo",
        "encuestas_realizadas": "Encuestas",
        "clasificacion_riesgo": "Nivel de riesgo",
        "progreso_guias": st.column_config.ProgressColumn(
            "Progreso en guías",
            min_value=0,
            max_value=100,
            format="%d%%"
        ),
        "recomendaciones_pendientes": "Pendientes"
    }
)


# =========================
# DETALLE DEL PARTICIPANTE
# =========================

st.write("")
st.markdown("### Detalle del participante")

if df_filtrado.empty:
    st.info("No hay participantes que coincidan con los filtros.")

else:
    opciones = {
        (
            f"{fila['nombre_completo']} — "
            f"{fila['ciudad']} — "
            f"{fila['id_participante'][:8]}"
        ): fila["id_participante"]

        for _, fila in df_filtrado.iterrows()
    }

    etiqueta_seleccionada = st.selectbox(
        "Selecciona un participante",
        opciones.keys()
    )

    participante_id = opciones[etiqueta_seleccionada]

    participante = df[
        df["id_participante"] == participante_id
    ].iloc[0]

    detalle1, detalle2, detalle3, detalle4 = st.columns(4)

    with detalle1:
        st.metric(
            "Encuestas realizadas",
            int(participante["encuestas_realizadas"])
        )

    with detalle2:
        st.metric(
            "Nivel de riesgo",
            participante["clasificacion_riesgo"]
        )

    with detalle3:
        st.metric(
            "Progreso en guías",
            f"{int(participante['progreso_guias'])}%"
        )

    with detalle4:
        st.metric(
            "Recomendaciones pendientes",
            int(participante["recomendaciones_pendientes"])
        )

    st.markdown(
        f"""
        <div class="participant-detail-card">
            <h3>{participante["nombre_completo"]}</h3>
            <p><b>Edad:</b> {participante["edad"]}</p>
            <p><b>Género:</b> {participante["genero"]}</p>
            <p><b>Ciudad:</b> {participante["ciudad"]}</p>
            <p><b>Nivel educativo:</b> {participante["nivel_educativo"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )