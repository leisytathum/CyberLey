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
    """
    Restaura la sesión del administrador.
    Realiza un segundo intento si Supabase tarda en responder.
    """

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

    with open(ruta_css, "r", encoding="utf-8") as archivo:
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


def registrar_reporte(
    tipo_reporte: str,
    descripcion: str
):
    """
    Registra en Supabase que el administrador generó un reporte.
    """

    supabase.table("reportes").insert({
        "generado_por": st.session_state["usuario_id"],
        "tipo_reporte": tipo_reporte,
        "descripcion": descripcion
    }).execute()


def convertir_booleanos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte True y False a Sí y No para que el CSV
    sea más fácil de interpretar.
    """

    df_exportar = df.copy()

    columnas_booleanas = [
        "usa_misma_contrasena",
        "usa_wifi_publico",
        "usa_doble_factor",
        "tiene_antivirus",
        "actualiza_contrasenas",
        "comparte_info_redes"
    ]

    for columna in columnas_booleanas:
        if columna in df_exportar.columns:
            df_exportar[columna] = (
                df_exportar[columna]
                .map({
                    True: "Sí",
                    False: "No"
                })
                .fillna("Sin registrar")
            )

    return df_exportar


def preparar_csv(
    df: pd.DataFrame
) -> bytes:
    """
    Convierte un DataFrame a CSV utilizando UTF-8 con BOM
    para facilitar su apertura en Excel.
    """

    contenido = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    return contenido.encode("utf-8-sig")


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

    encuestas = consultar_tabla(
        "encuestas",
        "id_encuesta, id_participante, fecha_aplicacion, estado"
    )

    resultados = consultar_tabla(
        "resultados_riesgo",
        (
            "id_resultado, id_encuesta, puntaje_riesgo, "
            "clasificacion_riesgo, observacion, fecha_calculo"
        )
    )

    respuestas = consultar_tabla(
        "respuestas_encuesta",
        (
            "id_respuesta, id_encuesta, usa_misma_contrasena, "
            "usa_wifi_publico, reconoce_phishing, usa_doble_factor, "
            "tiene_antivirus, actualiza_contrasenas, "
            "comparte_info_redes, nivel_conocimiento"
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


# =========================
# PREPARAR DATAFRAMES
# =========================

df_participantes = pd.DataFrame(participantes)
df_perfiles = pd.DataFrame(perfiles)
df_encuestas = pd.DataFrame(encuestas)
df_resultados = pd.DataFrame(resultados)
df_respuestas = pd.DataFrame(respuestas)


# Excluir administradores del reporte de participantes
if not df_participantes.empty and not df_perfiles.empty:

    df_participantes = df_participantes.merge(
        df_perfiles,
        left_on="id_usuario",
        right_on="id",
        how="left"
    )

    df_participantes = df_participantes[
        df_participantes["rol"] == "usuario"
    ].copy()


# Crear un DataFrame general
if df_participantes.empty:

    df_general = pd.DataFrame()

else:
    df_general = df_participantes.copy()

    if not df_encuestas.empty:
        df_general = df_general.merge(
            df_encuestas,
            on="id_participante",
            how="left"
        )

    if (
        not df_resultados.empty
        and "id_encuesta" in df_general.columns
    ):
        df_general = df_general.merge(
            df_resultados,
            on="id_encuesta",
            how="left"
        )

    if (
        not df_respuestas.empty
        and "id_encuesta" in df_general.columns
    ):
        df_general = df_general.merge(
            df_respuestas,
            on="id_encuesta",
            how="left"
        )


# Preparar columnas para filtros
if not df_general.empty:

    if "fecha_aplicacion" in df_general.columns:
        df_general["fecha_aplicacion"] = pd.to_datetime(
            df_general["fecha_aplicacion"],
            errors="coerce"
        )

    if "clasificacion_riesgo" in df_general.columns:
        df_general["clasificacion_riesgo"] = (
            df_general["clasificacion_riesgo"]
            .fillna("Sin evaluar")
            .str.title()
        )

    if "ciudad" in df_general.columns:
        df_general["ciudad"] = (
            df_general["ciudad"]
            .fillna("Sin registrar")
        )

    if "nivel_educativo" in df_general.columns:
        df_general["nivel_educativo"] = (
            df_general["nivel_educativo"]
            .fillna("Sin registrar")
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
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=6,
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
Filtra la información almacenada y descarga reportes
para apoyar el análisis de los hábitos digitales.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# VALIDAR DATOS
# =========================

if df_participantes.empty:
    st.info("Todavía no hay participantes registrados.")
    st.stop()


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
        "Respuestas de encuestas"
    ]
)

filtro1, filtro2, filtro3, filtro4 = st.columns(4)

with filtro1:
    ciudades = [
        "Todas"
    ] + sorted(
        df_participantes["ciudad"]
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
        df_participantes["nivel_educativo"]
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
        "Todos",
        "Sin evaluar",
        "Bajo",
        "Medio",
        "Alto"
    ]

    riesgo_seleccionado = st.selectbox(
        "Nivel de riesgo",
        niveles_riesgo
    )

with filtro4:

    if (
        not df_general.empty
        and "fecha_aplicacion" in df_general.columns
        and not df_general["fecha_aplicacion"]
        .dropna()
        .empty
    ):
        fechas_disponibles = (
            df_general["fecha_aplicacion"]
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

if not df_filtrado.empty:

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

    if (
        riesgo_seleccionado != "Todos"
        and "clasificacion_riesgo"
        in df_filtrado.columns
    ):
        df_filtrado = df_filtrado[
            df_filtrado["clasificacion_riesgo"]
            == riesgo_seleccionado
        ]

    if (
        isinstance(rango_fechas, tuple)
        and len(rango_fechas) == 2
        and "fecha_aplicacion" in df_filtrado.columns
    ):
        fecha_desde, fecha_hasta = rango_fechas

        filas_sin_encuesta = (
            df_filtrado["fecha_aplicacion"]
            .isna()
        )

        filas_en_rango = (
            df_filtrado["fecha_aplicacion"]
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
        "fecha_aplicacion",
        "puntaje_riesgo",
        "clasificacion_riesgo",
        "observacion"
    ]

elif tipo_reporte == "Respuestas de encuestas":

    columnas_reporte = [
        "nombre_completo",
        "ciudad",
        "fecha_aplicacion",
        "usa_misma_contrasena",
        "usa_wifi_publico",
        "reconoce_phishing",
        "usa_doble_factor",
        "tiene_antivirus",
        "actualiza_contrasenas",
        "comparte_info_redes",
        "nivel_conocimiento"
    ]

else:

    columnas_reporte = [
        "nombre_completo",
        "edad",
        "genero",
        "ciudad",
        "nivel_educativo",
        "fecha_aplicacion",
        "estado",
        "puntaje_riesgo",
        "clasificacion_riesgo",
        "observacion"
    ]


# Mostrar solamente las columnas disponibles
columnas_disponibles = [
    columna
    for columna in columnas_reporte
    if columna in df_filtrado.columns
]

df_reporte = df_filtrado[
    columnas_disponibles
].copy()

df_reporte = convertir_booleanos(
    df_reporte
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