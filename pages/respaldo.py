import gzip
import json
import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from httpx import ConnectError, TimeoutException
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Respaldo y recuperación",
    page_icon="💾",
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
# NOTIFICACIONES
# =========================

def mostrar_toast(
    mensaje: str,
    icono: str = "✅"
):
    st.toast(
        mensaje,
        icon=icono,
        duration=4
    )


# =========================
# TABLAS RESPALDADAS
# =========================

TABLAS_RESPALDO = [
    "participantes",
    "encuestas",
    "respuestas_encuesta",
    "resultados_riesgo"
]


# =========================
# FUNCIONES DE RESPALDO
# =========================

def consultar_tabla(
    nombre_tabla: str
) -> list[dict]:

    respuesta = (
        supabase
        .table(nombre_tabla)
        .select("*")
        .execute()
    )

    return respuesta.data or []


def generar_respaldo_binario() -> bytes:
    """
    Consulta los datos y crea un archivo binario comprimido.
    """

    contenido = {
        "metadata": {
            "sistema": "CyberLey",
            "version": "1.0",
            "fecha_generacion": datetime.now().isoformat(),
            "tablas_incluidas": TABLAS_RESPALDO
        },
        "datos": {}
    }

    for tabla in TABLAS_RESPALDO:
        contenido["datos"][tabla] = consultar_tabla(
            tabla
        )

    contenido_json = json.dumps(
        contenido,
        ensure_ascii=False,
        indent=2,
        default=str
    )

    return gzip.compress(
        contenido_json.encode("utf-8")
    )


def leer_respaldo_binario(
    archivo_binario: bytes
) -> dict:
    """
    Lee y valida un respaldo generado por CyberLey.
    """

    try:
        contenido_json = gzip.decompress(
            archivo_binario
        ).decode("utf-8")

        respaldo = json.loads(
            contenido_json
        )

    except Exception as error:
        raise ValueError(
            "El archivo no es un respaldo válido de CyberLey."
        ) from error

    if not isinstance(respaldo, dict):
        raise ValueError(
            "El contenido del respaldo no tiene el formato esperado."
        )

    metadata = respaldo.get("metadata", {})
    datos = respaldo.get("datos", {})

    if metadata.get("sistema") != "CyberLey":
        raise ValueError(
            "El archivo no pertenece al sistema CyberLey."
        )

    for tabla in TABLAS_RESPALDO:
        if tabla not in datos:
            raise ValueError(
                f"El respaldo no contiene la tabla requerida: {tabla}."
            )

        if not isinstance(datos[tabla], list):
            raise ValueError(
                f"Los datos de la tabla {tabla} no son válidos."
            )

    return respaldo


def restaurar_respaldo(
    respaldo: dict
) -> dict[str, int]:
    """
    Restaura registros usando upsert.
    No borra información existente.
    """

    datos = respaldo["datos"]

    orden_restauracion = [
        "participantes",
        "encuestas",
        "respuestas_encuesta",
        "resultados_riesgo"
    ]

    registros_restaurados = {}

    for tabla in orden_restauracion:

        filas = datos.get(tabla, [])

        if filas:
            (
                supabase
                .table(tabla)
                .upsert(filas)
                .execute()
            )

        registros_restaurados[tabla] = len(filas)

    return registros_restaurados


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

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")
    
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
<h1>Respaldo y recuperación</h1>
<p>
Genera copias de seguridad binarias y recupera
los datos analíticos del sistema cuando sea necesario.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# INFORMACIÓN GENERAL
# =========================

st.info(
    "El respaldo incluye participantes, encuestas, respuestas "
    "y resultados de riesgo. No incluye contraseñas ni cuentas "
    "de autenticación."
)


# =========================
# GENERAR RESPALDO
# =========================

st.markdown("### Generar respaldo")

st.write(
    "Descarga una copia comprimida de los datos actuales. "
    "El archivo puede almacenarse de forma segura para "
    "utilizarlo posteriormente."
)

if st.button(
    "Preparar respaldo binario",
    use_container_width=True
):

    try:
        respaldo_binario = generar_respaldo_binario()

        st.session_state["respaldo_binario"] = (
            respaldo_binario
        )

        mostrar_toast(
            "Respaldo generado correctamente.",
            "✅"
        )

    except Exception as error:
        st.error(
            "No se pudo generar el respaldo."
        )

        st.write(error)


if "respaldo_binario" in st.session_state:

    fecha_archivo = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.download_button(
        label="⬇️ Descargar respaldo",
        data=st.session_state["respaldo_binario"],
        file_name=(
            f"backup_cyberley_{fecha_archivo}.json.gz"
        ),
        mime="application/gzip",
        use_container_width=True
    )


st.divider()


# =========================
# RESTAURAR RESPALDO
# =========================

st.markdown("### Restaurar respaldo")

st.write(
    "Sube un respaldo generado previamente por CyberLey. "
    "La restauración agregará o actualizará registros sin "
    "eliminar información existente."
)

archivo_subido = st.file_uploader(
    "Selecciona un archivo de respaldo",
    type=["gz"]
)

if archivo_subido is not None:

    try:
        contenido_archivo = archivo_subido.getvalue()

        respaldo_validado = leer_respaldo_binario(
            contenido_archivo
        )

        metadata = respaldo_validado["metadata"]
        datos = respaldo_validado["datos"]

        st.success(
            "✅ El archivo tiene una estructura válida."
        )

        st.markdown("#### Resumen del respaldo")

        st.write(
            f"**Sistema:** {metadata.get('sistema')}"
        )

        st.write(
            f"**Fecha de generación:** "
            f"{metadata.get('fecha_generacion')}"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Participantes",
                len(datos["participantes"])
            )

        with col2:
            st.metric(
                "Encuestas",
                len(datos["encuestas"])
            )

        with col3:
            st.metric(
                "Respuestas",
                len(datos["respuestas_encuesta"])
            )

        with col4:
            st.metric(
                "Resultados",
                len(datos["resultados_riesgo"])
            )

        confirmar = st.checkbox(
            "Confirmo que revisé el respaldo y deseo restaurarlo."
        )

        if st.button(
            "Restaurar datos",
            use_container_width=True,
            disabled=not confirmar
        ):

            try:
                resumen = restaurar_respaldo(
                    respaldo_validado
                )

                mostrar_toast(
                    "Datos restaurados correctamente.",
                    "✅"
                )

                st.success(
                    "✅ La recuperación se completó correctamente."
                )

                st.json(resumen)

            except Exception as error:
                st.error(
                    "No se pudieron restaurar los datos."
                )

                st.write(error)

    except Exception as error:
        st.error(
            "El archivo seleccionado no es válido."
        )

        st.write(error)