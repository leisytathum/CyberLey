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
    page_title="CyberLey | Participantes",
    page_icon="👥",
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
# VALIDAR SESIÓN
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
# CONSULTAS
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


def preparar_datos_participantes() -> pd.DataFrame:

    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, id_usuario, nombre_completo, edad, "
            "genero, ciudad, nivel_educativo, fecha_registro"
        )
    )

    perfiles = consultar_tabla(
        "perfiles",
        "id, rol"
    )

    respuestas = consultar_tabla(
        "respuestas_encuesta_ciberseguridad",
        (
            "id_respuesta, id_usuario, fecha_respuesta, "
            "usa_nube, plataforma_nube, nivel_conocimiento, "
            "reconoce_phishing, estado_antivirus, "
            "reutiliza_contrasenas, tipo_conexion, "
            "puntaje_riesgo, clasificacion_riesgo, observacion"
        )
    )

    if not participantes:
        return pd.DataFrame()

    df_participantes = pd.DataFrame(
        participantes
    )

    df_perfiles = pd.DataFrame(
        perfiles
    )

    df_respuestas = pd.DataFrame(
        respuestas
    )

    # Excluir administradores
    if not df_perfiles.empty:

        df_participantes = df_participantes.merge(
            df_perfiles,
            left_on="id_usuario",
            right_on="id",
            how="left"
        )

        df_participantes = df_participantes[
            df_participantes["rol"] == "usuario"
        ].copy()

    # Si no hay respuestas todavía
    if df_respuestas.empty:

        df_participantes["encuestas_realizadas"] = 0
        df_participantes["fecha_ultima_evaluacion"] = None
        df_participantes["puntaje_riesgo"] = None
        df_participantes["clasificacion_riesgo"] = "Sin Evaluar"
        df_participantes["nivel_conocimiento"] = "Sin evaluar"
        df_participantes["reconoce_phishing"] = "Sin evaluar"
        df_participantes["estado_antivirus"] = "Sin evaluar"
        df_participantes["reutiliza_contrasenas"] = "Sin evaluar"
        df_participantes["observacion"] = "Sin evaluación registrada."

        return df_participantes

    df_respuestas["fecha_respuesta"] = pd.to_datetime(
        df_respuestas["fecha_respuesta"],
        errors="coerce"
    )

    df_respuestas["puntaje_riesgo"] = pd.to_numeric(
        df_respuestas["puntaje_riesgo"],
        errors="coerce"
    )

    # Cantidad de encuestas por usuario
    cantidad_encuestas = (
        df_respuestas
        .groupby("id_usuario")
        .size()
        .reset_index(name="encuestas_realizadas")
    )

    # Última encuesta por usuario
    ultimas_respuestas = (
        df_respuestas
        .sort_values("fecha_respuesta")
        .drop_duplicates(
            subset=["id_usuario"],
            keep="last"
        )
        [
            [
                "id_usuario",
                "fecha_respuesta",
                "puntaje_riesgo",
                "clasificacion_riesgo",
                "nivel_conocimiento",
                "reconoce_phishing",
                "estado_antivirus",
                "reutiliza_contrasenas",
                "tipo_conexion",
                "observacion"
            ]
        ]
        .rename(
            columns={
                "fecha_respuesta": "fecha_ultima_evaluacion"
            }
        )
    )

    df_participantes = df_participantes.merge(
        cantidad_encuestas,
        on="id_usuario",
        how="left"
    )

    df_participantes = df_participantes.merge(
        ultimas_respuestas,
        on="id_usuario",
        how="left"
    )

    # Limpieza final
    df_participantes["encuestas_realizadas"] = (
        df_participantes["encuestas_realizadas"]
        .fillna(0)
        .astype(int)
    )

    df_participantes["clasificacion_riesgo"] = (
        df_participantes["clasificacion_riesgo"]
        .fillna("Sin Evaluar")
        .str.title()
    )

    for columna in [
        "nivel_conocimiento",
        "reconoce_phishing",
        "estado_antivirus",
        "reutiliza_contrasenas",
        "tipo_conexion"
    ]:
        if columna in df_participantes.columns:
            df_participantes[columna] = (
                df_participantes[columna]
                .fillna("Sin evaluar")
            )

    df_participantes["observacion"] = (
        df_participantes["observacion"]
        .fillna("Sin evaluación registrada.")
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
            "🧹 Limpieza de datos",
            "📥 Importar datos históricos",
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=1,
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

elif menu == "📝 Encuestas":
    st.switch_page("pages/encuestas.py")

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
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Participantes</h1>
<p>
Consulta los usuarios registrados, revisa si completaron la encuesta
y analiza su último resultado de riesgo digital.
</p>
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
    st.error(
        "No se pudieron cargar los participantes."
    )
    st.write(error)
    st.stop()


if df.empty:
    st.info("Todavía no hay participantes registrados.")
    st.stop()


# =========================
# MÉTRICAS
# =========================

total_participantes = len(df)

participantes_evaluados = len(
    df[
        df["encuestas_realizadas"] > 0
    ]
)

pendientes_encuesta = total_participantes - participantes_evaluados

riesgo_alto = len(
    df[
        df["clasificacion_riesgo"] == "Alto"
    ]
)

promedio_riesgo = (
    round(
        df["puntaje_riesgo"]
        .dropna()
        .mean(),
        1
    )
    if not df["puntaje_riesgo"].dropna().empty
    else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Participantes",
        total_participantes
    )

with col2:
    st.metric(
        "Evaluados",
        participantes_evaluados
    )

with col3:
    st.metric(
        "Pendientes",
        pendientes_encuesta
    )

with col4:
    st.metric(
        "Riesgo alto",
        riesgo_alto
    )

with col5:
    st.metric(
        "Promedio riesgo",
        promedio_riesgo
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
    ciudades = [
        "Todas"
    ] + sorted(
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
    niveles = [
        "Todos"
    ] + sorted(
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
        df_filtrado["clasificacion_riesgo"] == riesgo_seleccionado
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
    "fecha_ultima_evaluacion",
    "puntaje_riesgo",
    "clasificacion_riesgo"
]

columnas_existentes = [
    columna
    for columna in columnas_tabla
    if columna in df_filtrado.columns
]

df_tabla = df_filtrado[
    columnas_existentes
].copy()

if "fecha_ultima_evaluacion" in df_tabla.columns:
    df_tabla["fecha_ultima_evaluacion"] = pd.to_datetime(
        df_tabla["fecha_ultima_evaluacion"],
        errors="coerce"
    ).dt.strftime("%d/%m/%Y")

df_tabla = df_tabla.rename(
    columns={
        "nombre_completo": "Nombre completo",
        "edad": "Edad",
        "ciudad": "Ciudad",
        "nivel_educativo": "Nivel educativo",
        "encuestas_realizadas": "Encuestas",
        "fecha_ultima_evaluacion": "Última evaluación",
        "puntaje_riesgo": "Puntaje",
        "clasificacion_riesgo": "Nivel de riesgo"
    }
)

st.dataframe(
    df_tabla,
    use_container_width=True,
    hide_index=True
)


# =========================
# DETALLE DEL PARTICIPANTE
# =========================

st.write("")

st.markdown("### Detalle del participante")

if df_filtrado.empty:
    st.info(
        "No hay participantes que coincidan con los filtros."
    )

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

    participante_id = opciones[
        etiqueta_seleccionada
    ]

    participante = df[
        df["id_participante"] == participante_id
    ].iloc[0]

    detalle1, detalle2, detalle3, detalle4 = st.columns(4)

    with detalle1:
        st.metric(
            "Encuestas realizadas",
            int(
                participante["encuestas_realizadas"]
            )
        )

    with detalle2:
        st.metric(
            "Nivel de riesgo",
            participante["clasificacion_riesgo"]
        )

    with detalle3:
        st.metric(
            "Puntaje",
            (
                int(participante["puntaje_riesgo"])
                if pd.notna(
                    participante["puntaje_riesgo"]
                )
                else "Sin evaluar"
            )
        )

    with detalle4:
        st.metric(
            "Reconoce phishing",
            participante.get(
                "reconoce_phishing",
                "Sin evaluar"
            )
        )

    st.markdown(
        f"""
<div class="participant-detail-card">
<h3>{participante["nombre_completo"]}</h3>
<p><b>Edad:</b> {participante.get("edad", "No disponible")}</p>
<p><b>Género:</b> {participante.get("genero", "No disponible")}</p>
<p><b>Ciudad:</b> {participante.get("ciudad", "No disponible")}</p>
<p><b>Nivel educativo:</b> {participante.get("nivel_educativo", "No disponible")}</p>
<p><b>Nivel de conocimiento:</b> {participante.get("nivel_conocimiento", "Sin evaluar")}</p>
<p><b>Antivirus:</b> {participante.get("estado_antivirus", "Sin evaluar")}</p>
<p><b>Reutiliza contraseñas:</b> {participante.get("reutiliza_contrasenas", "Sin evaluar")}</p>
<p><b>Tipo de conexión:</b> {participante.get("tipo_conexion", "Sin evaluar")}</p>
<p><b>Observación:</b> {participante.get("observacion", "Sin evaluación registrada.")}</p>
</div>
""",
        unsafe_allow_html=True
    )