import os
import time
from datetime import date, datetime
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
    page_title="CyberLey | Reportes",
    page_icon="📄",
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


def registrar_reporte(
    tipo_reporte: str,
    descripcion: str
):
    """
    Registra en Supabase que el administrador generó un reporte.
    """

    try:
        supabase.table("reportes").insert({
            "generado_por": st.session_state["usuario_id"],
            "tipo_reporte": tipo_reporte,
            "descripcion": descripcion
        }).execute()

    except Exception:
        pass


def preparar_csv(
    df: pd.DataFrame
) -> bytes:

    contenido = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    return contenido.encode("utf-8-sig")


def preparar_dataframe_general(
    participantes: list[dict],
    perfiles: list[dict],
    respuestas: list[dict]
) -> pd.DataFrame:

    df_participantes = pd.DataFrame(
        participantes
    )

    df_perfiles = pd.DataFrame(
        perfiles
    )

    df_respuestas = pd.DataFrame(
        respuestas
    )

    if df_participantes.empty:
        return pd.DataFrame()

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

    # Unir participantes con respuestas nuevas
    if not df_respuestas.empty:
        df_general = df_participantes.merge(
            df_respuestas,
            on="id_usuario",
            how="left"
        )

    else:
        df_general = df_participantes.copy()

    # Fechas
    if "fecha_respuesta" in df_general.columns:
        df_general["fecha_respuesta"] = pd.to_datetime(
            df_general["fecha_respuesta"],
            errors="coerce"
        )

    if "fecha_registro" in df_general.columns:
        df_general["fecha_registro"] = pd.to_datetime(
            df_general["fecha_registro"],
            errors="coerce"
        )

    # Puntaje
    if "puntaje_riesgo" in df_general.columns:
        df_general["puntaje_riesgo"] = pd.to_numeric(
            df_general["puntaje_riesgo"],
            errors="coerce"
        )

    # Clasificación
    if "clasificacion_riesgo" in df_general.columns:
        df_general["clasificacion_riesgo"] = (
            df_general["clasificacion_riesgo"]
            .fillna("Sin evaluar")
            .str.title()
        )
    else:
        df_general["clasificacion_riesgo"] = "Sin evaluar"

    # Valores por defecto
    for columna in [
        "ciudad",
        "nivel_educativo",
        "genero"
    ]:
        if columna in df_general.columns:
            df_general[columna] = (
                df_general[columna]
                .fillna("Sin registrar")
            )

    return df_general


# =========================
# CARGAR DATOS
# =========================

try:
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

    historial_reportes = (
        supabase
        .table("reportes")
        .select(
            "tipo_reporte, descripcion, fecha_generacion"
        )
        .order(
            "fecha_generacion",
            desc=True
        )
        .execute()
        .data
        or []
    )

except Exception as error:
    st.error("No se pudieron cargar los datos para generar reportes.")
    st.write(error)
    st.stop()


df_general = preparar_dataframe_general(
    participantes,
    perfiles,
    respuestas_ciberseguridad
)


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
        index=7,
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

elif menu == "📥 Importar datos históricos":
    st.switch_page("pages/importar_datos.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Reportes</h1>
<p>
Filtra la información almacenada y descarga reportes sobre participantes,
encuestas de ciberseguridad, resultados de riesgo y hábitos digitales.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# VALIDAR DATOS
# =========================

if df_general.empty:
    st.info("Todavía no hay participantes registrados.")
    st.stop()


# =========================
# MÉTRICAS GENERALES
# =========================

total_participantes = df_general["id_usuario"].nunique()

total_evaluaciones = (
    df_general["id_respuesta"]
    .dropna()
    .nunique()
    if "id_respuesta" in df_general.columns
    else 0
)

promedio_riesgo = (
    round(
        df_general["puntaje_riesgo"]
        .dropna()
        .mean(),
        1
    )
    if "puntaje_riesgo" in df_general.columns
    and not df_general["puntaje_riesgo"].dropna().empty
    else 0
)

riesgo_alto = (
    len(
        df_general[
            df_general["clasificacion_riesgo"] == "Alto"
        ]
    )
    if "clasificacion_riesgo" in df_general.columns
    else 0
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        "Participantes",
        total_participantes
    )

with col_m2:
    st.metric(
        "Evaluaciones",
        total_evaluaciones
    )

with col_m3:
    st.metric(
        "Promedio riesgo",
        promedio_riesgo
    )

with col_m4:
    st.metric(
        "Riesgo alto",
        riesgo_alto
    )


# =========================
# FILTROS
# =========================

st.markdown("### Configurar reporte")

tipo_reporte = st.selectbox(
    "Tipo de reporte",
    [
        "Reporte general",
        "Participantes registrados",
        "Resultados de riesgo",
        "Respuestas de encuestas",
        "Hábitos digitales"
    ]
)

filtro1, filtro2, filtro3, filtro4 = st.columns(4)

with filtro1:
    ciudades = [
        "Todas"
    ] + sorted(
        df_general["ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad_seleccionada = st.selectbox(
        "Ciudad",
        ciudades
    )

with filtro2:
    niveles_educativos = [
        "Todos"
    ] + sorted(
        df_general["nivel_educativo"]
        .dropna()
        .unique()
        .tolist()
    )

    nivel_educativo_seleccionado = st.selectbox(
        "Nivel educativo",
        niveles_educativos
    )

with filtro3:
    niveles_riesgo = [
        "Todos"
    ] + sorted(
        df_general["clasificacion_riesgo"]
        .dropna()
        .unique()
        .tolist()
    )

    riesgo_seleccionado = st.selectbox(
        "Nivel de riesgo",
        niveles_riesgo
    )

with filtro4:

    if (
        "fecha_respuesta" in df_general.columns
        and not df_general["fecha_respuesta"]
        .dropna()
        .empty
    ):
        fechas_disponibles = (
            df_general["fecha_respuesta"]
            .dropna()
            .dt.date
        )

        fecha_inicial = fechas_disponibles.min()
        fecha_final = fechas_disponibles.max()

    else:
        fecha_inicial = date.today()
        fecha_final = date.today()

    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(
            fecha_inicial,
            fecha_final
        )
    )


# =========================
# APLICAR FILTROS
# =========================

df_filtrado = df_general.copy()

if ciudad_seleccionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["ciudad"]
        == ciudad_seleccionada
    ]

if nivel_educativo_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["nivel_educativo"]
        == nivel_educativo_seleccionado
    ]

if riesgo_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["clasificacion_riesgo"]
        == riesgo_seleccionado
    ]

if (
    isinstance(rango_fechas, tuple)
    and len(rango_fechas) == 2
    and "fecha_respuesta" in df_filtrado.columns
):
    fecha_desde, fecha_hasta = rango_fechas

    filas_sin_encuesta = (
        df_filtrado["fecha_respuesta"]
        .isna()
    )

    filas_en_rango = (
        df_filtrado["fecha_respuesta"]
        .dt.date
        .between(
            fecha_desde,
            fecha_hasta
        )
    )

    df_filtrado = df_filtrado[
        filas_sin_encuesta
        | filas_en_rango
    ]


# =========================
# SELECCIONAR COLUMNAS
# =========================

if tipo_reporte == "Participantes registrados":

    columnas_reporte = [
        "nombre_completo",
        "edad",
        "genero",
        "ciudad",
        "nivel_educativo",
        "fecha_registro"
    ]

elif tipo_reporte == "Resultados de riesgo":

    columnas_reporte = [
        "nombre_completo",
        "ciudad",
        "nivel_educativo",
        "fecha_respuesta",
        "puntaje_riesgo",
        "clasificacion_riesgo",
        "observacion"
    ]

elif tipo_reporte == "Respuestas de encuestas":

    columnas_reporte = [
        "nombre_completo",
        "ciudad",
        "nivel_educativo",
        "fecha_respuesta",
        "usa_nube",
        "plataforma_nube",
        "contenido_nube",
        "nivel_conocimiento",
        "manejo_ciberseguridad",
        "frecuencia_info_seguridad",
        "reconoce_phishing",
        "identifica_herramientas_seguridad",
        "estado_antivirus",
        "tipo_conexion",
        "estabilidad_conexion",
        "frecuencia_fallas_internet",
        "cambio_contrasenas_anual",
        "reutiliza_contrasenas",
        "importancia_actualizar_contrasenas"
    ]

elif tipo_reporte == "Hábitos digitales":

    columnas_reporte = [
        "nombre_completo",
        "nivel_conocimiento",
        "reconoce_phishing",
        "estado_antivirus",
        "cambio_contrasenas_anual",
        "reutiliza_contrasenas",
        "frecuencia_info_seguridad",
        "tipo_conexion",
        "puntaje_riesgo",
        "clasificacion_riesgo"
    ]

else:

    columnas_reporte = [
        "nombre_completo",
        "edad",
        "genero",
        "ciudad",
        "nivel_educativo",
        "fecha_registro",
        "fecha_respuesta",
        "usa_nube",
        "nivel_conocimiento",
        "reconoce_phishing",
        "estado_antivirus",
        "reutiliza_contrasenas",
        "puntaje_riesgo",
        "clasificacion_riesgo",
        "observacion"
    ]


columnas_disponibles = [
    columna
    for columna in columnas_reporte
    if columna in df_filtrado.columns
]

df_reporte = df_filtrado[
    columnas_disponibles
].copy()


# =========================
# RENOMBRAR COLUMNAS
# =========================

df_reporte = df_reporte.rename(
    columns={
        "nombre_completo": "Participante",
        "edad": "Edad",
        "genero": "Género",
        "ciudad": "Ciudad",
        "nivel_educativo": "Nivel educativo",
        "fecha_registro": "Fecha de registro",
        "fecha_respuesta": "Fecha de respuesta",
        "usa_nube": "Usa nube",
        "plataforma_nube": "Plataforma de nube",
        "contenido_nube": "Contenido en nube",
        "nivel_conocimiento": "Nivel de conocimiento",
        "manejo_ciberseguridad": "Manejo de ciberseguridad",
        "frecuencia_info_seguridad": "Frecuencia de información de seguridad",
        "reconoce_phishing": "Reconoce phishing",
        "identifica_herramientas_seguridad": "Identifica herramientas de seguridad",
        "estado_antivirus": "Estado del antivirus",
        "tipo_conexion": "Tipo de conexión",
        "estabilidad_conexion": "Estabilidad de conexión",
        "frecuencia_fallas_internet": "Frecuencia de fallas de internet",
        "cambio_contrasenas_anual": "Cambio de contraseñas anual",
        "reutiliza_contrasenas": "Reutiliza contraseñas",
        "importancia_actualizar_contrasenas": "Importancia de actualizar contraseñas",
        "puntaje_riesgo": "Puntaje de riesgo",
        "clasificacion_riesgo": "Clasificación de riesgo",
        "observacion": "Observación"
    }
)


# =========================
# VISTA PREVIA
# =========================

st.write("")
st.markdown("### Vista previa")

st.caption(
    f"El reporte contiene {len(df_reporte)} filas."
)

if df_reporte.empty:
    st.info(
        "No existen datos que coincidan con los filtros seleccionados."
    )

else:
    st.dataframe(
        df_reporte,
        use_container_width=True,
        hide_index=True
    )


# =========================
# PREPARAR DESCARGA
# =========================

if st.button(
    "Preparar reporte",
    use_container_width=True,
    disabled=df_reporte.empty
):

    try:
        csv_binario = preparar_csv(
            df_reporte
        )

        fecha_archivo = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        nombre_archivo = (
            tipo_reporte
            .lower()
            .replace(" ", "_")
        )

        st.session_state["reporte_csv"] = (
            csv_binario
        )

        st.session_state["reporte_nombre_archivo"] = (
            f"{nombre_archivo}_{fecha_archivo}.csv"
        )

        descripcion = (
            f"Ciudad: {ciudad_seleccionada}; "
            f"Nivel educativo: {nivel_educativo_seleccionado}; "
            f"Riesgo: {riesgo_seleccionado}; "
            f"Filas exportadas: {len(df_reporte)}"
        )

        registrar_reporte(
            tipo_reporte,
            descripcion
        )

        st.toast(
            "Reporte preparado correctamente.",
            icon="✅"
        )

    except Exception as error:
        st.error(
            "No se pudo preparar el reporte."
        )

        st.write(error)


if (
    "reporte_csv" in st.session_state
    and "reporte_nombre_archivo"
    in st.session_state
):

    st.download_button(
        label="⬇️ Descargar reporte CSV",
        data=st.session_state["reporte_csv"],
        file_name=(
            st.session_state[
                "reporte_nombre_archivo"
            ]
        ),
        mime="text/csv",
        use_container_width=True
    )


# =========================
# HISTORIAL DE REPORTES
# =========================

st.divider()

st.markdown("### Historial de reportes generados")

if not historial_reportes:
    st.info(
        "Todavía no se han generado reportes."
    )

else:
    df_historial = pd.DataFrame(
        historial_reportes
    )

    if "fecha_generacion" in df_historial.columns:
        df_historial["fecha_generacion"] = pd.to_datetime(
            df_historial["fecha_generacion"],
            errors="coerce"
        ).dt.strftime(
            "%d/%m/%Y %H:%M"
        )

    st.dataframe(
        df_historial,
        use_container_width=True,
        hide_index=True,
        column_config={
            "tipo_reporte": "Tipo de reporte",
            "descripcion": "Filtros aplicados",
            "fecha_generacion": "Fecha de generación"
        }
    )