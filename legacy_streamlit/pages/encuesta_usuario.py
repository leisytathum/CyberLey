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
# VALIDAR SESIÓN
# =========================

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")


# =========================
# CARGAR CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "styles.css"

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

def calcular_riesgo(
    nivel_conocimiento,
    manejo_ciberseguridad,
    frecuencia_info_seguridad,
    reconoce_phishing,
    identifica_herramientas_seguridad,
    estado_antivirus,
    estabilidad_conexion,
    frecuencia_fallas_internet,
    cambio_contrasenas_anual,
    reutiliza_contrasenas,
    importancia_actualizar_contrasenas
):
    """
    Calcula un puntaje de riesgo digital.
    Mayor puntaje = mayor riesgo.
    """

    puntaje = 0

    # Nivel de conocimiento
    if nivel_conocimiento == "Bajo":
        puntaje += 20
    elif nivel_conocimiento == "Medio":
        puntaje += 10
    elif nivel_conocimiento == "Alto":
        puntaje += 0

    # Manejo de ciberseguridad
    if manejo_ciberseguridad <= 2:
        puntaje += 15
    elif manejo_ciberseguridad == 3:
        puntaje += 8
    else:
        puntaje += 0

    # Información sobre seguridad
    if frecuencia_info_seguridad == "Nunca":
        puntaje += 12
    elif frecuencia_info_seguridad == "Rara vez":
        puntaje += 8
    elif frecuencia_info_seguridad == "A veces":
        puntaje += 4

    # Phishing
    if reconoce_phishing == "No":
        puntaje += 15
    elif reconoce_phishing == "A veces":
        puntaje += 8

    # Herramientas de seguridad
    if identifica_herramientas_seguridad == "No":
        puntaje += 10
    elif identifica_herramientas_seguridad == "A veces":
        puntaje += 5

    # Antivirus
    if estado_antivirus == "No tengo antivirus":
        puntaje += 15
    elif estado_antivirus == "Tengo antivirus, pero no está actualizado":
        puntaje += 10
    elif estado_antivirus == "No sé":
        puntaje += 8

    # Estabilidad de conexión
    if estabilidad_conexion <= 2:
        puntaje += 8
    elif estabilidad_conexion == 3:
        puntaje += 4

    # Fallas de internet
    if frecuencia_fallas_internet == "Frecuentemente":
        puntaje += 8
    elif frecuencia_fallas_internet == "A veces":
        puntaje += 4

    # Cambio de contraseñas
    if cambio_contrasenas_anual == "Nunca":
        puntaje += 15
    elif cambio_contrasenas_anual == "Una vez al año":
        puntaje += 8
    elif cambio_contrasenas_anual == "Cada 6 meses":
        puntaje += 4

    # Reutilización de contraseñas
    if reutiliza_contrasenas == "Sí":
        puntaje += 15
    elif reutiliza_contrasenas == "A veces":
        puntaje += 8

    # Importancia de actualizar contraseñas
    if importancia_actualizar_contrasenas <= 2:
        puntaje += 8
    elif importancia_actualizar_contrasenas == 3:
        puntaje += 4

    # Clasificación
    if puntaje >= 70:
        clasificacion = "alto"

        observacion = (
            "Presentas un nivel de riesgo alto. Es recomendable "
            "fortalecer tus prácticas de seguridad digital, actualizar "
            "contraseñas, evitar reutilizarlas y mejorar la identificación "
            "de amenazas como phishing."
        )

    elif puntaje >= 35:
        clasificacion = "medio"

        observacion = (
            "Presentas un nivel de riesgo medio. Tienes algunas buenas "
            "prácticas, pero aún existen hábitos que pueden mejorar para "
            "reducir tu exposición a riesgos digitales."
        )

    else:
        clasificacion = "bajo"

        observacion = (
            "Presentas un nivel de riesgo bajo. Tus hábitos digitales son "
            "adecuados, aunque siempre es importante mantener buenas "
            "prácticas de ciberseguridad."
        )

    return puntaje, clasificacion, observacion


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="survey-heading">
<span class="survey-badge">Evaluación CyberLey</span>
<h1>Encuesta de hábitos digitales y ciberseguridad</h1>
<p>
Responde las siguientes preguntas para analizar tu nivel de riesgo digital
y conocer recomendaciones de seguridad.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# FORMULARIO
# =========================

with st.form("formulario_encuesta_ciberseguridad"):

    st.markdown("### 1. Uso de servicios digitales")

    usa_nube = st.radio(
        "¿Utilizas alguna plataforma de almacenamiento en la nube?",
        [
            "Sí",
            "No"
        ]
    )

    if usa_nube == "Sí":
        plataforma_nube = st.selectbox(
            "¿Qué plataforma de almacenamiento en la nube utilizas principalmente?",
            [
                "Google Drive",
                "OneDrive",
                "Dropbox",
                "iCloud",
                "Mega",
                "Otra"
            ]
        )

        contenido_nube = st.selectbox(
            "¿Qué tipo de información guardas principalmente en la nube?",
            [
                "Documentos personales",
                "Fotos o videos",
                "Archivos académicos",
                "Archivos laborales",
                "Contraseñas o información sensible",
                "Otro"
            ]
        )

    else:
        plataforma_nube = "No aplica"
        contenido_nube = "No aplica"

    st.markdown("### 2. Conocimiento sobre ciberseguridad")

    nivel_conocimiento = st.selectbox(
        "¿Cómo consideras tu nivel de conocimiento sobre ciberseguridad?",
        [
            "Bajo",
            "Medio",
            "Alto"
        ]
    )

    manejo_ciberseguridad = st.slider(
        "Del 1 al 5, ¿cómo calificas tu manejo de prácticas de ciberseguridad?",
        min_value=1,
        max_value=5,
        value=3
    )

    frecuencia_info_seguridad = st.selectbox(
        "¿Con qué frecuencia recibes o buscas información sobre seguridad digital?",
        [
            "Nunca",
            "Rara vez",
            "A veces",
            "Frecuentemente"
        ]
    )

    reconoce_phishing = st.selectbox(
        "¿Puedes reconocer intentos de phishing o correos sospechosos?",
        [
            "Sí",
            "No",
            "A veces"
        ]
    )

    identifica_herramientas_seguridad = st.selectbox(
        "¿Identificas herramientas básicas de seguridad digital?",
        [
            "Sí",
            "No",
            "A veces"
        ]
    )

    st.markdown("### 3. Seguridad del dispositivo")

    estado_antivirus = st.selectbox(
        "¿Cuál es el estado del antivirus en tu dispositivo principal?",
        [
            "Tengo antivirus actualizado",
            "Tengo antivirus, pero no está actualizado",
            "No tengo antivirus",
            "No sé"
        ]
    )

    st.markdown("### 4. Conexión a internet")

    tipo_conexion = st.selectbox(
        "¿Qué tipo de conexión a internet utilizas principalmente?",
        [
            "Wi-Fi",
            "Router",
            "Datos móviles",
            "Fibra óptica",
            "ADSL",
            "Satelital",
            "Otro"
        ]
    )

    estabilidad_conexion = st.slider(
        "Del 1 al 5, ¿cómo calificas la estabilidad de tu conexión a internet?",
        min_value=1,
        max_value=5,
        value=3
    )

    frecuencia_fallas_internet = st.selectbox(
        "¿Con qué frecuencia presentas fallas de internet?",
        [
            "Nunca",
            "Rara vez",
            "A veces",
            "Frecuentemente"
        ]
    )

    st.markdown("### 5. Contraseñas")

    cambio_contrasenas_anual = st.selectbox(
        "¿Con qué frecuencia cambias tus contraseñas durante el año?",
        [
            "Nunca",
            "Una vez al año",
            "Cada 6 meses",
            "Cada 3 meses o menos"
        ]
    )

    reutiliza_contrasenas = st.selectbox(
        "¿Reutilizas la misma contraseña en varias cuentas?",
        [
            "Sí",
            "No",
            "A veces"
        ]
    )

    importancia_actualizar_contrasenas = st.slider(
        "Del 1 al 5, ¿qué tan importante consideras actualizar tus contraseñas anualmente?",
        min_value=1,
        max_value=5,
        value=3
    )

    enviar = st.form_submit_button(
        "Enviar encuesta",
        use_container_width=True
    )


# =========================
# GUARDAR RESPUESTA
# =========================

if enviar:

    try:
        puntaje_riesgo, clasificacion_riesgo, observacion = calcular_riesgo(
            nivel_conocimiento,
            manejo_ciberseguridad,
            frecuencia_info_seguridad,
            reconoce_phishing,
            identifica_herramientas_seguridad,
            estado_antivirus,
            estabilidad_conexion,
            frecuencia_fallas_internet,
            cambio_contrasenas_anual,
            reutiliza_contrasenas,
            importancia_actualizar_contrasenas
        )

        datos_respuesta = {
            "id_usuario": st.session_state["usuario_id"],
            "usa_nube": usa_nube,
            "plataforma_nube": plataforma_nube,
            "contenido_nube": contenido_nube,
            "nivel_conocimiento": nivel_conocimiento,
            "manejo_ciberseguridad": manejo_ciberseguridad,
            "frecuencia_info_seguridad": frecuencia_info_seguridad,
            "reconoce_phishing": reconoce_phishing,
            "identifica_herramientas_seguridad": identifica_herramientas_seguridad,
            "estado_antivirus": estado_antivirus,
            "tipo_conexion": tipo_conexion,
            "estabilidad_conexion": estabilidad_conexion,
            "frecuencia_fallas_internet": frecuencia_fallas_internet,
            "cambio_contrasenas_anual": cambio_contrasenas_anual,
            "reutiliza_contrasenas": reutiliza_contrasenas,
            "importancia_actualizar_contrasenas": importancia_actualizar_contrasenas,
            "puntaje_riesgo": puntaje_riesgo,
            "clasificacion_riesgo": clasificacion_riesgo,
            "observacion": observacion
        }

        supabase.table(
            "respuestas_encuesta_ciberseguridad"
        ).insert(
            datos_respuesta
        ).execute()

        st.success("Encuesta enviada correctamente.")

        st.markdown(
            f"""
<div class="risk-result {clasificacion_riesgo}">
<p>Tu puntaje de riesgo digital es:</p>
<h2>{puntaje_riesgo} puntos</h2>
<h3>Clasificación: {clasificacion_riesgo.upper()}</h3>
<span>{observacion}</span>
</div>
""",
            unsafe_allow_html=True
        )

    except Exception as error:
        st.error("No se pudo guardar la encuesta.")
        st.write(error)