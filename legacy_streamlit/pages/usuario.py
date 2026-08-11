import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Usuario",
    page_icon="🛡️",
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
# CSS VISUAL
# =========================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(139, 92, 246, 0.13), transparent 30%),
        radial-gradient(circle at bottom right, rgba(239, 35, 60, 0.10), transparent 32%),
        #f8fafc;
}

.block-container {
    padding-top: 36px;
    padding-bottom: 40px;
}

[data-testid="stHeader"] {
    background: transparent;
}

.user-hero {
    background:
        linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(239, 35, 60, 0.08)),
        #ffffff;
    border: 1px solid #eee7ff;
    border-radius: 24px;
    padding: 28px 30px;
    margin-bottom: 24px;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.07);
}

.user-badge {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #ede9fe;
    color: #7c3aed;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 12px;
}

.user-hero h1 {
    margin: 0;
    color: #111827;
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -0.6px;
}

.user-hero p {
    margin-top: 10px;
    color: #64748b;
    font-size: 15px;
    line-height: 1.7;
    max-width: 850px;
}

.result-card {
    background: #ffffff;
    border: 1px solid #e8edf5;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
    margin-bottom: 24px;
}

.result-title {
    color: #111827;
    font-size: 25px;
    font-weight: 900;
    margin-bottom: 18px;
}

.result-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 18px;
}

.result-box {
    border-radius: 18px;
    padding: 18px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
}

.result-box span {
    display: block;
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
}

.result-box strong {
    color: #111827;
    font-size: 30px;
    font-weight: 900;
}

.risk-message {
    border-radius: 18px;
    padding: 18px 20px;
    font-size: 14px;
    line-height: 1.6;
    font-weight: 600;
}

.risk-message.alto {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}

.risk-message.medio {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
}

.risk-message.bajo {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
}

.summary-title {
    color: #111827;
    font-size: 25px;
    font-weight: 900;
    margin: 10px 0 18px 0;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.answer-card {
    background: #ffffff;
    border: 1px solid #e8edf5;
    border-radius: 18px;
    padding: 18px;
    min-height: 122px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.answer-icon {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ede9fe;
    margin-bottom: 12px;
    font-size: 21px;
}

.answer-card span {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.answer-card p {
    color: #111827;
    font-size: 15px;
    font-weight: 800;
    margin: 6px 0 0 0;
    line-height: 1.4;
}

.actions-card {
    background: #ffffff;
    border: 1px solid #e8edf5;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.stButton > button {
    min-height: 48px;
    border-radius: 15px;
    border: none;
    font-weight: 850;
    color: white;
    background: linear-gradient(90deg, #8b5cf6, #ef233c);
    box-shadow: 0 12px 24px rgba(139, 92, 246, 0.18);
}

.stButton > button:hover {
    color: white;
    opacity: 0.94;
}

.logout-button button {
    background: #0f172a !important;
}

@media (max-width: 1000px) {
    .result-grid,
    .summary-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True
)


# =========================
# DATOS DEL USUARIO
# =========================

nombre = st.session_state.get(
    "nombre",
    "Usuario"
)

usuario_id = st.session_state.get(
    "usuario_id"
)


# =========================
# CONSULTAR ÚLTIMO RESULTADO
# =========================

try:
    respuesta = (
        supabase
        .table("respuestas_encuesta_ciberseguridad")
        .select("*")
        .eq("id_usuario", usuario_id)
        .order(
            "fecha_respuesta",
            desc=True
        )
        .limit(1)
        .execute()
    )

    datos = respuesta.data or []

except Exception as error:
    st.error("No se pudo cargar tu información de riesgo.")
    st.write(error)
    datos = []


# =========================
# ENCABEZADO
# =========================

st.markdown(
    f"""
<div class="user-hero">
<span class="user-badge">Panel de usuario</span>
<h1>¡Hola, {nombre}! 👋</h1>
<p>
Consulta tu resultado más reciente de ciberseguridad, revisa tus hábitos digitales
y completa una nueva evaluación cuando desees actualizar tu nivel de riesgo.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# SIN ENCUESTA
# =========================

if not datos:

    st.markdown(
        """
<div class="result-card">
<div class="result-title">Aún no tienes una evaluación registrada</div>
<p>
Completa la encuesta de ciberseguridad para conocer tu puntaje,
clasificación de riesgo y recomendaciones personalizadas.
</p>
</div>
""",
        unsafe_allow_html=True
    )

    if st.button(
        "Completar encuesta de ciberseguridad",
        use_container_width=True
    ):
        st.switch_page("pages/encuesta_usuario.py")


# =========================
# CON RESULTADO
# =========================

else:

    ultimo_resultado = datos[0]

    puntaje = ultimo_resultado.get(
        "puntaje_riesgo",
        0
    )

    clasificacion = ultimo_resultado.get(
        "clasificacion_riesgo",
        "sin clasificar"
    )

    observacion = ultimo_resultado.get(
        "observacion",
        "Sin observación disponible."
    )

    fecha = str(
        ultimo_resultado.get(
            "fecha_respuesta",
            "Sin fecha"
        )
    )[:10]

    if clasificacion == "alto":
        icono_riesgo = "⚠️"
        texto_estado = "Riesgo alto"
    elif clasificacion == "medio":
        icono_riesgo = "🛡️"
        texto_estado = "Riesgo medio"
    elif clasificacion == "bajo":
        icono_riesgo = "✅"
        texto_estado = "Riesgo bajo"
    else:
        icono_riesgo = "📊"
        texto_estado = "Sin clasificar"

    st.markdown(
        f"""
<div class="result-card">
<div class="result-title">Tu resultado más reciente</div>

<div class="result-grid">
<div class="result-box">
<span>Puntaje de riesgo</span>
<strong>{puntaje}</strong>
</div>

<div class="result-box">
<span>Clasificación</span>
<strong>{clasificacion.upper()}</strong>
</div>

<div class="result-box">
<span>Fecha de evaluación</span>
<strong>{fecha}</strong>
</div>
</div>

<div class="risk-message {clasificacion}">
{icono_riesgo} <strong>{texto_estado}.</strong> {observacion}
</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="summary-title">
Resumen de tus respuestas
</div>
""",
        unsafe_allow_html=True
    )

    respuestas_cards = [
        (
            "🧠",
            "Conocimiento",
            ultimo_resultado.get(
                "nivel_conocimiento",
                "No disponible"
            )
        ),
        (
            "🎣",
            "Reconoce phishing",
            ultimo_resultado.get(
                "reconoce_phishing",
                "No disponible"
            )
        ),
        (
            "🛡️",
            "Antivirus",
            ultimo_resultado.get(
                "estado_antivirus",
                "No disponible"
            )
        ),
        (
            "🔑",
            "Reutiliza contraseñas",
            ultimo_resultado.get(
                "reutiliza_contrasenas",
                "No disponible"
            )
        ),
        (
            "☁️",
            "Usa nube",
            ultimo_resultado.get(
                "usa_nube",
                "No disponible"
            )
        ),
        (
            "📁",
            "Plataforma",
            ultimo_resultado.get(
                "plataforma_nube",
                "No disponible"
            )
        ),
        (
            "🌐",
            "Conexión",
            ultimo_resultado.get(
                "tipo_conexion",
                "No disponible"
            )
        ),
        (
            "📶",
            "Fallas de internet",
            ultimo_resultado.get(
                "frecuencia_fallas_internet",
                "No disponible"
            )
        )
    ]

    html_cards = '<div class="summary-grid">'

    for icono, titulo, valor in respuestas_cards:
        html_cards += f"""
<div class="answer-card">
<div class="answer-icon">{icono}</div>
<span>{titulo}</span>
<p>{valor}</p>
</div>
"""

    html_cards += "</div>"

    st.markdown(
        html_cards,
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="actions-card">
""",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Realizar nueva encuesta",
            use_container_width=True
        ):
            st.switch_page("pages/encuesta_usuario.py")

    with col2:
        if st.button(
            "Cerrar sesión",
            use_container_width=True
        ):
            st.session_state.clear()
            st.switch_page("app.py")

    st.markdown(
        """
</div>
""",
        unsafe_allow_html=True
    )