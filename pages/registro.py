import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
from httpx import ReadTimeout
from pathlib import Path

load_dotenv()

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="CyberLey | Registro",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)
ROOT_DIR = Path(__file__).resolve().parents[1]

def cargar_css():
    with open(ROOT_DIR / "css" / "styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


cargar_css()

# =========================
# DISEÑO EN DOS COLUMNAS
# =========================
ROOT_DIR = Path(__file__).resolve().parents[1]

col1, col2 = st.columns([1.1, 1])


# =========================
# COLUMNA IZQUIERDA
# =========================

with col1:

    st.image(
        str(ROOT_DIR / "Logo.png"),
        width=260
    )

    st.markdown(
        """
        <h1 class="brand-title">CyberLey</h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p class="brand-description">
            Crea una cuenta para acceder al sistema de análisis
            de hábitos digitales y ciberseguridad.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="feature-box">
            🚀 Evalúa tus hábitos digitales y recibe recomendaciones
            para mejorar tu seguridad en línea.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# COLUMNA DERECHA
# =========================

with col2:

    st.markdown(
        """
        <h2 class="form-title">Crear cuenta</h2>
        <p class="form-subtitle">
            Completa tus datos para acceder a CyberLey.
        </p>
        """,
        unsafe_allow_html=True
    )

    nombre_completo = st.text_input(
        "Nombre completo",
        placeholder="Ejemplo: Ana Martínez"
    )

    edad = st.number_input(
        "Edad",
        min_value=10,
        max_value=100,
        step=1
    )

    genero = st.selectbox(
        "Género",
        [
            "Seleccionar",
            "Femenino",
            "Masculino",
            "Prefiero no responder",
            "Otro"
        ]
    )

    ciudad = st.text_input(
        "Ciudad",
        placeholder="Ejemplo: La Ceiba"
    )

    nivel_educativo = st.selectbox(
        "Nivel educativo",
        [
            "Seleccionar",
            "Secundaria",
            "Universidad",
            "Técnico",
            "Posgrado",
            "Otro"
        ]
    )

    nuevo_email = st.text_input(
        "Correo electrónico",
        placeholder="correo@ejemplo.com"
    )

    nueva_password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button(
        "Crear cuenta",
        use_container_width=True
    ):

        if (
            nombre_completo.strip() == ""
            or ciudad.strip() == ""
            or nuevo_email.strip() == ""
            or nueva_password == ""
        ):
            st.warning("Completa todos los campos.")

        elif genero == "Seleccionar":
            st.warning("Selecciona tu género.")

        elif nivel_educativo == "Seleccionar":
            st.warning("Selecciona tu nivel educativo.")

        elif len(nueva_password) < 6:
            st.warning(
                "La contraseña debe tener al menos 6 caracteres."
            )

        else:
            try:
                supabase.auth.sign_up({
                    "email": nuevo_email.strip(),
                    "password": nueva_password,
                    "options": {
                        "data": {
                            "nombre_completo": nombre_completo.strip(),
                            "edad": int(edad),
                            "genero": genero,
                            "ciudad": ciudad.strip(),
                            "nivel_educativo": nivel_educativo
                        }
                    }
                })

                st.toast(
                    "Cuenta creada correctamente. Ya puedes iniciar sesión.",
                    icon="✅",
                    duration=5
                )

            except ReadTimeout:
                st.success(
                    "✅ La solicitud de registro fue procesada."
                )

                st.info(
                    "Supabase tardó en responder. "
                    "La cuenta podría haberse creado correctamente. "
                    "Vuelve al inicio e intenta iniciar sesión."
                )

            except Exception as error:
                st.error(
                    "❌ No se pudo completar el registro. "
                    "Verifica los datos o intenta nuevamente."
                )
                st.write(error)

    if st.button(
        "Volver a iniciar sesión",
        use_container_width=True
    ):
        st.switch_page("app.py")