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
    page_title="CyberLey | Limpieza de datos",
    page_icon="🧹",
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
    supabase.auth.set_session(
        access_token,
        refresh_token
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

    with open(ruta_css, "r", encoding="utf-8") as archivo:
        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()
# =========================
# NOTIFICACIONES TEMPORALES
# =========================

def guardar_notificacion(
    mensaje: str,
    icono: str = "✅"
):
    """
    Guarda una notificación para mostrarla después de recargar la página.
    """
    st.session_state["toast_mensaje"] = mensaje
    st.session_state["toast_icono"] = icono


def mostrar_notificacion_pendiente():
    """
    Muestra la notificación una sola vez y luego la elimina.
    """
    mensaje = st.session_state.pop(
        "toast_mensaje",
        None
    )

    icono = st.session_state.pop(
        "toast_icono",
        "✅"
    )

    if mensaje:
        st.toast(
            mensaje,
            icon=icono,
            duration=4
        )


mostrar_notificacion_pendiente()

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
# FUNCIONES DE LIMPIEZA
# =========================

def normalizar_texto(valor) -> str:
    """
    Elimina espacios al inicio, al final y repetidos.
    También aplica formato de título.

    Ejemplo:
    '  la   ceiba ' -> 'La Ceiba'
    """

    if valor is None:
        return ""

    texto = str(valor).strip()

    if texto == "":
        return ""

    return " ".join(texto.split()).title()


def normalizar_genero(valor) -> str:
    """
    Normaliza variantes comunes de género.
    """

    texto = normalizar_texto(valor)

    equivalencias = {
        "Femenino": "Femenino",
        "Masculino": "Masculino",
        "Otro": "Otro",
        "Prefiero No Responder": "Prefiero no responder"
    }

    return equivalencias.get(texto, texto)


def normalizar_nivel_educativo(valor) -> str:
    """
    Normaliza variantes comunes del nivel educativo.
    """

    texto = normalizar_texto(valor)

    equivalencias = {
        "Secundaria": "Secundaria",
        "Universidad": "Universidad",
        "Técnico": "Técnico",
        "Tecnico": "Técnico",
        "Posgrado": "Posgrado",
        "Otro": "Otro"
    }

    return equivalencias.get(texto, texto)


def preparar_cambios(df_participantes: pd.DataFrame) -> pd.DataFrame:
    """
    Compara valores actuales con valores limpios y genera
    una vista previa de los cambios seguros.
    """

    cambios = []

    for _, fila in df_participantes.iterrows():

        nombre_original = fila.get("nombre_completo")
        ciudad_original = fila.get("ciudad")
        genero_original = fila.get("genero")
        nivel_original = fila.get("nivel_educativo")

        nombre_limpio = normalizar_texto(nombre_original)
        ciudad_limpia = normalizar_texto(ciudad_original)
        genero_limpio = normalizar_genero(genero_original)
        nivel_limpio = normalizar_nivel_educativo(nivel_original)

        datos_actualizados = {}

        if nombre_limpio and nombre_limpio != nombre_original:
            datos_actualizados["nombre_completo"] = nombre_limpio

        if ciudad_limpia and ciudad_limpia != ciudad_original:
            datos_actualizados["ciudad"] = ciudad_limpia

        if genero_limpio and genero_limpio != genero_original:
            datos_actualizados["genero"] = genero_limpio

        if nivel_limpio and nivel_limpio != nivel_original:
            datos_actualizados["nivel_educativo"] = nivel_limpio

        if datos_actualizados:
            cambios.append({
                "id_participante": fila["id_participante"],
                "Nombre actual": nombre_original,
                "Nombre limpio": nombre_limpio,
                "Ciudad actual": ciudad_original,
                "Ciudad limpia": ciudad_limpia,
                "Género actual": genero_original,
                "Género limpio": genero_limpio,
                "Nivel actual": nivel_original,
                "Nivel limpio": nivel_limpio,
                "_datos_actualizados": datos_actualizados
            })

    return pd.DataFrame(cambios)


def aplicar_cambios(df_cambios: pd.DataFrame) -> int:
    """
    Actualiza únicamente las filas con correcciones seguras.
    """

    total_actualizados = 0

    for _, fila in df_cambios.iterrows():

        datos_actualizados = fila["_datos_actualizados"]

        if datos_actualizados:
            (
                supabase
                .table("participantes")
                .update(datos_actualizados)
                .eq(
                    "id_participante",
                    fila["id_participante"]
                )
                .execute()
            )

            total_actualizados += 1

    return total_actualizados


# =========================
# CARGAR DATOS
# =========================

try:
    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, id_usuario, nombre_completo, "
            "edad, genero, ciudad, nivel_educativo, fecha_registro"
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

    respuestas = consultar_tabla(
        "respuestas_encuesta",
        "id_respuesta, id_encuesta"
    )

    resultados = consultar_tabla(
        "resultados_riesgo",
        "id_resultado, id_encuesta"
    )

except Exception as error:
    st.error("No se pudieron cargar los datos.")
    st.write(error)
    st.stop()


# =========================
# FILTRAR SOLO PARTICIPANTES
# =========================

df_participantes = pd.DataFrame(participantes)
df_perfiles = pd.DataFrame(perfiles)

if not df_participantes.empty and not df_perfiles.empty:

    df_participantes = df_participantes.merge(
        df_perfiles,
        left_on="id_usuario",
        right_on="id",
        how="left"
    )

    # No incluir administradores en el análisis
    df_participantes = df_participantes[
        df_participantes["rol"] == "usuario"
    ].copy()


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
        index=4,
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
    
elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")
    
elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")
    
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
<h1>Limpieza de datos</h1>
<p>
Detecta problemas de calidad, revisa una vista previa
y aplica correcciones seguras antes del análisis.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# VALIDAR DATOS DISPONIBLES
# =========================

if df_participantes.empty:
    st.info("Todavía no existen participantes para analizar.")
    st.stop()


# =========================
# DETECTAR PROBLEMAS
# =========================

columnas_obligatorias = [
    "nombre_completo",
    "edad",
    "genero",
    "ciudad",
    "nivel_educativo"
]

campos_vacios = (
    df_participantes[columnas_obligatorias]
    .isna()
    .sum()
    .sum()
)

for columna in columnas_obligatorias:
    if df_participantes[columna].dtype == "object":
        campos_vacios += (
            df_participantes[columna]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

edades_invalidas = df_participantes[
    (df_participantes["edad"] < 10)
    | (df_participantes["edad"] > 100)
]

df_participantes["_nombre_normalizado"] = (
    df_participantes["nombre_completo"]
    .fillna("")
    .apply(normalizar_texto)
)

df_participantes["_ciudad_normalizada"] = (
    df_participantes["ciudad"]
    .fillna("")
    .apply(normalizar_texto)
)

duplicados = df_participantes[
    df_participantes.duplicated(
        subset=[
            "_nombre_normalizado",
            "edad",
            "_ciudad_normalizada"
        ],
        keep=False
    )
].copy()

df_encuestas = pd.DataFrame(encuestas)
df_respuestas = pd.DataFrame(respuestas)
df_resultados = pd.DataFrame(resultados)

encuestas_incompletas = pd.DataFrame()

if not df_encuestas.empty:

    ids_con_respuestas = set()

    if not df_respuestas.empty:
        ids_con_respuestas = set(
            df_respuestas["id_encuesta"].dropna()
        )

    ids_con_resultado = set()

    if not df_resultados.empty:
        ids_con_resultado = set(
            df_resultados["id_encuesta"].dropna()
        )

    encuestas_incompletas = df_encuestas[
        ~df_encuestas["id_encuesta"].isin(ids_con_respuestas)
        | ~df_encuestas["id_encuesta"].isin(ids_con_resultado)
    ].copy()

df_cambios = preparar_cambios(df_participantes)


# =========================
# MÉTRICAS
# =========================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Participantes analizados",
        len(df_participantes)
    )

with col2:
    st.metric(
        "Campos vacíos",
        int(campos_vacios)
    )

with col3:
    st.metric(
        "Posibles duplicados",
        len(duplicados)
    )

with col4:
    st.metric(
        "Encuestas incompletas",
        len(encuestas_incompletas)
    )

with col5:
    st.metric(
        "Filas por normalizar",
        len(df_cambios)
    )


st.write("")


# =========================
# PESTAÑAS
# =========================

tab_resumen, tab_correcciones, tab_duplicados, tab_encuestas = st.tabs(
    [
        "📊 Resumen",
        "🧹 Vista previa de limpieza",
        "🔎 Posibles duplicados",
        "📝 Encuestas incompletas"
    ]
)


# =========================
# TAB: RESUMEN
# =========================

with tab_resumen:

    st.markdown("### Calidad general de los datos")

    st.write(
        "La limpieza automática solamente normaliza textos. "
        "No elimina participantes ni modifica respuestas de encuestas."
    )

    columnas_mostrar = [
        "nombre_completo",
        "edad",
        "genero",
        "ciudad",
        "nivel_educativo",
        "fecha_registro"
    ]

    st.dataframe(
        df_participantes[columnas_mostrar],
        use_container_width=True,
        hide_index=True,
        column_config={
            "nombre_completo": "Nombre completo",
            "edad": "Edad",
            "genero": "Género",
            "ciudad": "Ciudad",
            "nivel_educativo": "Nivel educativo",
            "fecha_registro": "Fecha de registro"
        }
    )


# =========================
# TAB: VISTA PREVIA
# =========================

with tab_correcciones:

    st.markdown("### Correcciones seguras disponibles")

    if df_cambios.empty:
        st.success(
            "✅ Los textos ya tienen un formato uniforme. "
            "No hay cambios pendientes."
        )

    else:
        columnas_vista_previa = [
            "Nombre actual",
            "Nombre limpio",
            "Ciudad actual",
            "Ciudad limpia",
            "Género actual",
            "Género limpio",
            "Nivel actual",
            "Nivel limpio"
        ]

        st.dataframe(
            df_cambios[columnas_vista_previa],
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "Revisa la vista previa antes de aplicar los cambios."
        )

        confirmar = st.checkbox(
            "Confirmo que revisé las correcciones."
        )

        if st.button(
            "Aplicar limpieza segura",
            use_container_width=True,
            disabled=not confirmar
        ):
            try:
                total_actualizados = aplicar_cambios(
                    df_cambios
                )

                guardar_notificacion(
                    f"Se actualizaron {total_actualizados} participantes correctamente.",
                    "✅"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "No se pudieron aplicar las correcciones."
                )
                st.write(error)


# =========================
# TAB: DUPLICADOS
# =========================

with tab_duplicados:

    st.markdown("### Posibles registros duplicados")

    if duplicados.empty:
        st.success(
            "✅ No se detectaron posibles duplicados."
        )

    else:
        st.warning(
            "Estos registros podrían corresponder a la misma persona. "
            "No se eliminarán automáticamente."
        )

        st.dataframe(
            duplicados[
                [
                    "nombre_completo",
                    "edad",
                    "ciudad",
                    "nivel_educativo",
                    "fecha_registro"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB: ENCUESTAS INCOMPLETAS
# =========================

with tab_encuestas:

    st.markdown("### Encuestas incompletas")

    if encuestas_incompletas.empty:
        st.success(
            "✅ Todas las encuestas tienen respuestas y resultado."
        )

    else:
        st.warning(
            "Estas encuestas no tienen respuestas o todavía "
            "no poseen un resultado calculado."
        )

        st.dataframe(
            encuestas_incompletas,
            use_container_width=True,
            hide_index=True
        )