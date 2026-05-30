import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
load_dotenv()


# =========================
# CONFIGURACIÓN SUPABASE
# =========================

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# DISEÑO DE LA PÁGINA
# =========================

st.set_page_config(
    page_title="CyberLey Login",
    page_icon="🔐",
    layout="centered"
)
def cargar_css():
    with open("css/styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css()

col1, col2 = st.columns([1.1, 1])

with col1:

    st.image("Logo.png", width=260)

    st.markdown("""
    <h1 class="brand-title">CyberLey</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p class="brand-description">
        Plataforma para el análisis de hábitos digitales,
        evaluación de riesgos y fortalecimiento de la cultura
        de ciberseguridad.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
        🔒 Identifica riesgos digitales y promueve buenas prácticas de seguridad.
    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <h2 class="form-title">Iniciar sesión</h2>
    <p class="form-subtitle">
        Accede al sistema.
    </p>
    """, unsafe_allow_html=True)

    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión", use_container_width=True):

        if email == "" or password == "":
            st.warning("Por favor ingresa correo y contraseña.")

        else:
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password
            })

            # Guardar tokens para conservar la sesión en las demás páginas
                if response.session:
                    st.session_state["access_token"] = response.session.access_token
                    st.session_state["refresh_token"] = response.session.refresh_token

                usuario_id = response.user.id

                perfil_response = (
                        supabase
                        .table("perfiles")
                        .select("nombre_completo, rol")
                        .eq("id", usuario_id)
                        .single()
                        .execute()
                    )

                perfil = perfil_response.data

                if not perfil:
                    st.error("No se encontró el perfil del usuario.")
                    st.stop()

                st.session_state["usuario"] = response.user.email
                st.session_state["usuario_id"] = usuario_id
                st.session_state["nombre"] = perfil["nombre_completo"]
                st.session_state["rol"] = perfil["rol"]

                if perfil["rol"] == "admin":
                        st.switch_page("pages/dashboard.py")
                else:
                        st.switch_page("pages/usuario.py")

            except Exception as e:
                st.error("❌ Error al iniciar sesión")
                st.write(e)

    if st.button("Crear cuenta nueva", use_container_width=True):
        st.switch_page("pages/registro.py")