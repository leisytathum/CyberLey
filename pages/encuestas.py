import os
from pathlib import Path

import pandas as pd
import streamlit as st
import time
from httpx import ConnectError, TimeoutException
from dotenv import load_dotenv
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

    with open(ruta_css, "r", encoding="utf-8") as archivo:
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
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=2,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")


# =========================
# NAVEGACIÓN
# =========================

if menu == "🏠 Inicio":
    st.switch_page("pages/dashboard.py")

elif menu == "👥 Participantes":
    st.switch_page("pages/participantes.py")

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")
    
elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")
    
elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")
    
elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")
# =========================
# CONSULTAR ENCUESTAS
# =========================

st.markdown("""
<div class="page-heading">
    <h1>Encuestas registradas</h1>
    <p>
        Consulta las evaluaciones completadas por los participantes
        y revisa sus resultados de riesgo.
    </p>
</div>
""", unsafe_allow_html=True)

try:
    respuesta = (
        supabase
        .table("encuestas")
        .select(
            "id_encuesta, fecha_aplicacion, estado, "
            "participantes(nombre_completo, ciudad, nivel_educativo), "
            "resultados_riesgo(puntaje_riesgo, clasificacion_riesgo)"
        )
        .order("fecha_aplicacion", desc=True)
        .execute()
    )

    encuestas = respuesta.data or []

except Exception as error:
    st.error("No se pudieron consultar las encuestas.")
    st.write(error)
    encuestas = []


if not encuestas:
    st.info(
        "Todavía no hay encuestas completadas. "
        "Cuando un usuario responda la evaluación, aparecerá aquí."
    )

else:
    filas = []

    for encuesta in encuestas:
        participante = encuesta.get("participantes") or {}
        resultados = encuesta.get("resultados_riesgo") or []

        resultado = resultados[0] if resultados else {}

        filas.append({
            "Participante": participante.get(
                "nombre_completo",
                "Sin nombre"
            ),
            "Ciudad": participante.get(
                "ciudad",
                "Sin registrar"
            ),
            "Nivel educativo": participante.get(
                "nivel_educativo",
                "Sin registrar"
            ),
            "Fecha": encuesta.get("fecha_aplicacion"),
            "Estado": encuesta.get("estado"),
            "Puntaje": resultado.get("puntaje_riesgo", "Pendiente"),
            "Riesgo": resultado.get(
                "clasificacion_riesgo",
                "Sin calcular"
            )
        })

    df = pd.DataFrame(filas)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )