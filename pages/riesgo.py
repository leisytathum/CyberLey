import os
import time
from datetime import date
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
    """
    Restaura la sesión de Supabase.
    Si existe un problema temporal de conexión,
    realiza un segundo intento automáticamente.
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


# =========================
# CARGAR DATOS
# =========================

try:
    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, nombre_completo, edad, genero, "
            "ciudad, nivel_educativo"
        )
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
            "id_encuesta, usa_misma_contrasena, usa_wifi_publico, "
            "reconoce_phishing, usa_doble_factor, tiene_antivirus, "
            "actualiza_contrasenas, comparte_info_redes, "
            "nivel_conocimiento"
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
<h1>Análisis de riesgo</h1>
<p>
Explora los resultados de las evaluaciones, aplica filtros
y analiza los hábitos digitales que requieren mayor atención.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# VALIDAR DATOS
# =========================

if not resultados:
    st.info(
        "Todavía no existen resultados de riesgo. "
        "Cuando un usuario complete una encuesta, aparecerán aquí."
    )

    st.stop()


# =========================
# PREPARAR DATAFRAME PRINCIPAL
# =========================

df_participantes = pd.DataFrame(participantes)
df_encuestas = pd.DataFrame(encuestas)
df_resultados = pd.DataFrame(resultados)
df_respuestas = pd.DataFrame(respuestas)

df_resultados["puntaje_riesgo"] = pd.to_numeric(
    df_resultados["puntaje_riesgo"],
    errors="coerce"
)

df_resultados["fecha_calculo"] = pd.to_datetime(
    df_resultados["fecha_calculo"],
    errors="coerce"
)

df_encuestas["fecha_aplicacion"] = pd.to_datetime(
    df_encuestas["fecha_aplicacion"],
    errors="coerce"
)

df_analisis = (
    df_resultados
    .merge(
        df_encuestas,
        on="id_encuesta",
        how="left"
    )
    .merge(
        df_participantes,
        on="id_participante",
        how="left"
    )
)

df_analisis["nombre_completo"] = (
    df_analisis["nombre_completo"]
    .fillna("Participante sin nombre")
)

df_analisis["ciudad"] = (
    df_analisis["ciudad"]
    .fillna("Sin registrar")
)

df_analisis["nivel_educativo"] = (
    df_analisis["nivel_educativo"]
    .fillna("Sin registrar")
)

df_analisis["clasificacion_riesgo"] = (
    df_analisis["clasificacion_riesgo"]
    .fillna("sin calcular")
    .str.lower()
)


# =========================
# FILTROS
# =========================

st.markdown("### Filtros de análisis")

filtro1, filtro2, filtro3, filtro4 = st.columns(4)

with filtro1:
    nivel_riesgo = st.selectbox(
        "Clasificación de riesgo",
        [
            "Todos",
            "Alto",
            "Medio",
            "Bajo"
        ]
    )

with filtro2:
    ciudades = [
        "Todas"
    ] + sorted(
        df_analisis["ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad_seleccionada = st.selectbox(
        "Ciudad",
        ciudades
    )

with filtro3:
    niveles_educativos = [
        "Todos"
    ] + sorted(
        df_analisis["nivel_educativo"]
        .dropna()
        .unique()
        .tolist()
    )

    nivel_educativo_seleccionado = st.selectbox(
        "Nivel educativo",
        niveles_educativos
    )

with filtro4:
    fechas_disponibles = (
        df_analisis["fecha_aplicacion"]
        .dropna()
        .dt.date
    )

    if fechas_disponibles.empty:
        fecha_desde = date.today()
        fecha_hasta = date.today()

    else:
        fecha_desde = fechas_disponibles.min()
        fecha_hasta = fechas_disponibles.max()

    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(
            fecha_desde,
            fecha_hasta
        )
    )


# =========================
# APLICAR FILTROS
# =========================

df_filtrado = df_analisis.copy()

if nivel_riesgo != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["clasificacion_riesgo"]
        == nivel_riesgo.lower()
    ]

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

if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:

    fecha_inicial, fecha_final = rango_fechas

    df_filtrado = df_filtrado[
        (
            df_filtrado["fecha_aplicacion"]
            .dt.date
            >= fecha_inicial
        )
        &
        (
            df_filtrado["fecha_aplicacion"]
            .dt.date
            <= fecha_final
        )
    ]


# =========================
# MÉTRICAS PRINCIPALES
# =========================

total_resultados = len(df_filtrado)

puntaje_promedio = (
    round(
        df_filtrado["puntaje_riesgo"].mean(),
        1
    )
    if total_resultados > 0
    else 0
)

participantes_evaluados = (
    df_filtrado["id_participante"]
    .dropna()
    .nunique()
)

cantidad_alto = len(
    df_filtrado[
        df_filtrado["clasificacion_riesgo"]
        == "alto"
    ]
)

porcentaje_alto = (
    round(
        cantidad_alto
        / total_resultados
        * 100,
        1
    )
    if total_resultados > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Resultados analizados",
        total_resultados
    )

with col2:
    st.metric(
        "Participantes evaluados",
        participantes_evaluados
    )

with col3:
    st.metric(
        "Puntaje promedio",
        puntaje_promedio
    )

with col4:
    st.metric(
        "Resultados con riesgo alto",
        f"{porcentaje_alto}%"
    )


st.write("")


# =========================
# PESTAÑAS
# =========================

tab_resumen, tab_habitos, tab_tendencia, tab_detalle = st.tabs(
    [
        "📊 Distribución",
        "🔐 Hábitos inseguros",
        "📈 Tendencia",
        "📋 Resultados individuales"
    ]
)


# =========================
# TAB: DISTRIBUCIÓN
# =========================

with tab_resumen:

    st.markdown("### Distribución del nivel de riesgo")

    if df_filtrado.empty:
        st.info(
            "No existen resultados que coincidan con los filtros."
        )

    else:
        distribucion = (
            df_filtrado["clasificacion_riesgo"]
            .value_counts()
            .rename_axis("Nivel de riesgo")
            .reset_index(name="Cantidad")
        )

        distribucion["Nivel de riesgo"] = (
            distribucion["Nivel de riesgo"]
            .str.title()
        )

        st.bar_chart(
            distribucion,
            x="Nivel de riesgo",
            y="Cantidad",
            use_container_width=True
        )

        st.dataframe(
            distribucion,
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB: HÁBITOS INSEGUROS
# =========================

with tab_habitos:

    st.markdown("### Hábitos inseguros más frecuentes")

    ids_encuestas_filtradas = (
        df_filtrado["id_encuesta"]
        .dropna()
        .tolist()
    )

    if df_respuestas.empty or not ids_encuestas_filtradas:
        st.info(
            "No existen respuestas para analizar con los filtros actuales."
        )

    else:
        respuestas_filtradas = df_respuestas[
            df_respuestas["id_encuesta"]
            .isin(ids_encuestas_filtradas)
        ].copy()

        if respuestas_filtradas.empty:
            st.info(
                "No existen respuestas para analizar con los filtros actuales."
            )

        else:
            habitos = {
                "Usa la misma contraseña": int(
                    respuestas_filtradas[
                        "usa_misma_contrasena"
                    ].sum()
                ),
                "Usa Wi-Fi público": int(
                    respuestas_filtradas[
                        "usa_wifi_publico"
                    ].sum()
                ),
                "No reconoce phishing": int(
                    (
                        respuestas_filtradas[
                            "reconoce_phishing"
                        ]
                        != "si"
                    ).sum()
                ),
                "No usa doble factor": int(
                    (
                        ~respuestas_filtradas[
                            "usa_doble_factor"
                        ]
                    ).sum()
                ),
                "No tiene antivirus": int(
                    (
                        ~respuestas_filtradas[
                            "tiene_antivirus"
                        ]
                    ).sum()
                ),
                "No actualiza contraseñas": int(
                    (
                        ~respuestas_filtradas[
                            "actualiza_contrasenas"
                        ]
                    ).sum()
                ),
                "Comparte información en redes": int(
                    respuestas_filtradas[
                        "comparte_info_redes"
                    ].sum()
                )
            }

            df_habitos = (
                pd.DataFrame(
                    list(habitos.items()),
                    columns=[
                        "Hábito inseguro",
                        "Cantidad"
                    ]
                )
                .sort_values(
                    "Cantidad",
                    ascending=False
                )
            )

            st.bar_chart(
                df_habitos,
                x="Hábito inseguro",
                y="Cantidad",
                use_container_width=True
            )

            st.dataframe(
                df_habitos,
                use_container_width=True,
                hide_index=True
            )


# =========================
# TAB: TENDENCIA
# =========================

with tab_tendencia:

    st.markdown("### Tendencia de evaluaciones por fecha")

    if df_filtrado.empty:
        st.info(
            "No existen resultados que coincidan con los filtros."
        )

    else:
        tendencia = (
            df_filtrado
            .dropna(
                subset=[
                    "fecha_aplicacion"
                ]
            )
            .assign(
                fecha=lambda datos: (
                    datos["fecha_aplicacion"]
                    .dt.date
                )
            )
            .groupby(
                [
                    "fecha",
                    "clasificacion_riesgo"
                ]
            )
            .size()
            .unstack(
                fill_value=0
            )
            .sort_index()
        )

        tendencia.columns = [
            columna.title()
            for columna in tendencia.columns
        ]

        if tendencia.empty:
            st.info(
                "No existen fechas disponibles para mostrar la tendencia."
            )

        else:
            st.line_chart(
                tendencia,
                use_container_width=True
            )


# =========================
# TAB: RESULTADOS INDIVIDUALES
# =========================

with tab_detalle:

    st.markdown("### Resultados individuales")

    if df_filtrado.empty:
        st.info(
            "No existen resultados que coincidan con los filtros."
        )

    else:
        tabla_resultados = df_filtrado[
            [
                "nombre_completo",
                "ciudad",
                "nivel_educativo",
                "fecha_aplicacion",
                "puntaje_riesgo",
                "clasificacion_riesgo",
                "observacion"
            ]
        ].copy()

        tabla_resultados["clasificacion_riesgo"] = (
            tabla_resultados[
                "clasificacion_riesgo"
            ]
            .str.title()
        )

        tabla_resultados["fecha_aplicacion"] = (
            tabla_resultados[
                "fecha_aplicacion"
            ]
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        st.caption(
            f"Mostrando {len(tabla_resultados)} resultados."
        )

        st.dataframe(
            tabla_resultados,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nombre_completo": "Participante",
                "ciudad": "Ciudad",
                "nivel_educativo": "Nivel educativo",
                "fecha_aplicacion": "Fecha",
                "puntaje_riesgo": "Puntaje",
                "clasificacion_riesgo": "Clasificación",
                "observacion": "Observación"
            }
        )