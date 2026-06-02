import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Encuesta",
    page_icon="📝",
    layout="wide"
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
# VALIDAR USUARIO
# =========================

if "usuario_id" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

if st.session_state.get("rol") != "usuario":
    st.warning("Esta encuesta corresponde al panel de usuario.")
    st.switch_page("pages/dashboard.py")


# =========================
# CARGAR CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "styles.css"

    with open(ruta_css, "r", encoding="utf-8") as archivo:
        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()


# =========================
# FUNCIONES
# =========================

def obtener_participante():
    """
    Busca el participante relacionado con el usuario autenticado.
    """

    respuesta = (
        supabase
        .table("participantes")
        .select(
            "id_participante, nombre_completo"
        )
        .eq(
            "id_usuario",
            st.session_state["usuario_id"]
        )
        .execute()
    )

    datos = respuesta.data or []

    if not datos:
        return None

    return datos[0]


def convertir_si_no(valor: str) -> bool:
    """
    Convierte una respuesta de texto a booleano.
    """
    return valor == "Sí"


def calcular_riesgo(
    usa_misma_contrasena: bool,
    usa_wifi_publico: bool,
    reconoce_phishing: str,
    usa_doble_factor: bool,
    tiene_antivirus: bool,
    actualiza_contrasenas: bool,
    comparte_info_redes: bool
):
    """
    Calcula el puntaje y la clasificación de riesgo.
    """

    puntaje = 0

    if usa_misma_contrasena:
        puntaje += 2

    if usa_wifi_publico:
        puntaje += 2

    if reconoce_phishing == "no":
        puntaje += 2

    elif reconoce_phishing == "a_veces":
        puntaje += 1

    if not usa_doble_factor:
        puntaje += 2

    if not tiene_antivirus:
        puntaje += 1

    if not actualiza_contrasenas:
        puntaje += 1

    if comparte_info_redes:
        puntaje += 1

    if puntaje <= 3:
        clasificacion = "bajo"
        observacion = (
            "Mantienes buenos hábitos digitales. "
            "Continúa fortaleciendo tus prácticas de seguridad."
        )

    elif puntaje <= 7:
        clasificacion = "medio"
        observacion = (
            "Tienes algunos hábitos que podrían exponerte a riesgos. "
            "Revisa las recomendaciones disponibles."
        )

    else:
        clasificacion = "alto"
        observacion = (
            "Se identificaron varios hábitos inseguros. "
            "Es recomendable revisar las guías de ciberseguridad."
        )

    return puntaje, clasificacion, observacion


def guardar_encuesta(
    id_participante: str,
    respuestas: dict
):
    """
    Guarda encuesta, respuestas y resultado calculado.
    """

    puntaje, clasificacion, observacion = calcular_riesgo(
        usa_misma_contrasena=respuestas["usa_misma_contrasena"],
        usa_wifi_publico=respuestas["usa_wifi_publico"],
        reconoce_phishing=respuestas["reconoce_phishing"],
        usa_doble_factor=respuestas["usa_doble_factor"],
        tiene_antivirus=respuestas["tiene_antivirus"],
        actualiza_contrasenas=respuestas["actualiza_contrasenas"],
        comparte_info_redes=respuestas["comparte_info_redes"]
    )

    encuesta_response = (
        supabase
        .table("encuestas")
        .insert({
            "id_participante": id_participante,
            "estado": "completada"
        })
        .execute()
    )

    if not encuesta_response.data:
        raise ValueError(
            "No se pudo crear el registro de la encuesta."
        )

    id_encuesta = encuesta_response.data[0]["id_encuesta"]

    supabase.table("respuestas_encuesta").insert({
        "id_encuesta": id_encuesta,
        "usa_misma_contrasena": respuestas["usa_misma_contrasena"],
        "usa_wifi_publico": respuestas["usa_wifi_publico"],
        "reconoce_phishing": respuestas["reconoce_phishing"],
        "usa_doble_factor": respuestas["usa_doble_factor"],
        "tiene_antivirus": respuestas["tiene_antivirus"],
        "actualiza_contrasenas": respuestas["actualiza_contrasenas"],
        "comparte_info_redes": respuestas["comparte_info_redes"],
        "nivel_conocimiento": respuestas["nivel_conocimiento"]
    }).execute()

    supabase.table("resultados_riesgo").insert({
        "id_encuesta": id_encuesta,
        "puntaje_riesgo": puntaje,
        "clasificacion_riesgo": clasificacion,
        "observacion": observacion
    }).execute()

    return puntaje, clasificacion, observacion


# =========================
# OBTENER PARTICIPANTE
# =========================

try:
    participante = obtener_participante()

except Exception as error:
    st.error(
        "No se pudo consultar tu perfil de participante."
    )
    st.write(error)
    st.stop()

if not participante:
    st.error(
        "Tu cuenta existe, pero no tiene un perfil de participante asociado."
    )
    st.stop()


# =========================
# ENCABEZADO
# =========================

nombre = participante["nombre_completo"]

st.markdown(
    f"""
    <div class="survey-heading">
        <span class="survey-badge">Evaluación de hábitos digitales</span>
        <h1>Encuesta de ciberseguridad</h1>
        <p>
            Hola, <b>{nombre}</b>. Responde las siguientes preguntas
            para conocer tu nivel de riesgo digital.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# FORMULARIO
# =========================

with st.form("encuesta_ciberseguridad"):

    st.markdown("### Hábitos de seguridad")

    usa_misma_contrasena_texto = st.radio(
        "¿Usas la misma contraseña en varias cuentas?",
        ["No", "Sí"],
        horizontal=True
    )

    usa_wifi_publico_texto = st.radio(
        "¿Utilizas redes Wi-Fi públicas frecuentemente?",
        ["No", "Sí"],
        horizontal=True
    )

    reconoce_phishing_texto = st.selectbox(
        "¿Reconoces correos o mensajes sospechosos de phishing?",
        [
            "Seleccionar",
            "Sí",
            "A veces",
            "No"
        ]
    )

    usa_doble_factor_texto = st.radio(
        "¿Utilizas autenticación en dos pasos?",
        ["Sí", "No"],
        horizontal=True
    )

    tiene_antivirus_texto = st.radio(
        "¿Tienes antivirus o protección de seguridad activa?",
        ["Sí", "No"],
        horizontal=True
    )

    actualiza_contrasenas_texto = st.radio(
        "¿Actualizas tus contraseñas periódicamente?",
        ["Sí", "No"],
        horizontal=True
    )

    comparte_info_redes_texto = st.radio(
        "¿Compartes información personal en redes sociales?",
        ["No", "Sí"],
        horizontal=True
    )

    nivel_conocimiento_texto = st.selectbox(
        "¿Cómo consideras tu nivel de conocimiento en ciberseguridad?",
        [
            "Seleccionar",
            "Bajo",
            "Medio",
            "Alto"
        ]
    )

    enviar = st.form_submit_button(
        "Calcular mi nivel de riesgo",
        use_container_width=True
    )


# =========================
# GUARDAR RESPUESTAS
# =========================

if enviar:

    if reconoce_phishing_texto == "Seleccionar":
        st.warning(
            "Selecciona una respuesta para la pregunta sobre phishing."
        )

    elif nivel_conocimiento_texto == "Seleccionar":
        st.warning(
            "Selecciona tu nivel de conocimiento."
        )

    else:
        respuestas = {
            "usa_misma_contrasena": convertir_si_no(
                usa_misma_contrasena_texto
            ),
            "usa_wifi_publico": convertir_si_no(
                usa_wifi_publico_texto
            ),
            "reconoce_phishing": (
                reconoce_phishing_texto
                .lower()
                .replace(" ", "_")
            ),
            "usa_doble_factor": convertir_si_no(
                usa_doble_factor_texto
            ),
            "tiene_antivirus": convertir_si_no(
                tiene_antivirus_texto
            ),
            "actualiza_contrasenas": convertir_si_no(
                actualiza_contrasenas_texto
            ),
            "comparte_info_redes": convertir_si_no(
                comparte_info_redes_texto
            ),
            "nivel_conocimiento": (
                nivel_conocimiento_texto.lower()
            )
        }

        try:
            puntaje, clasificacion, observacion = guardar_encuesta(
                participante["id_participante"],
                respuestas
            )

            st.success(
                "✅ Encuesta completada correctamente."
            )

            st.markdown(
                f"""
                <div class="risk-result {clasificacion}">
                    <p>Tu resultado actual</p>
                    <h2>Riesgo {clasificacion.title()}</h2>
                    <h3>Puntaje: {puntaje} de 11</h3>
                    <span>{observacion}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as error:
            st.error(
                "No se pudo guardar la encuesta. "
                "Revisa la configuración de permisos en Supabase."
            )
            st.write(error)


# =========================
# NAVEGACIÓN
# =========================

st.write("")

col_volver, col_sesion = st.columns(2)

with col_volver:
    if st.button(
        "← Volver a mi panel",
        use_container_width=True
    ):
        st.switch_page("pages/usuario.py")

with col_sesion:
    if st.button(
        "Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.clear()
        st.switch_page("app.py")