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

# =========================
# ESTILOS
# =========================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f5ff 0%, #ffffff 45%, #fff5f5 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 480px;
    padding-top: 50px;
}

.login-card {
    background: white;
    padding: 35px;
    border-radius: 24px;
    box-shadow: 0px 12px 35px rgba(127, 90, 240, 0.18);
    border: 1px solid #eee7ff;
}

.title {
    text-align: center;
    color: #1f1f2e;
    font-size: 30px;
    font-weight: 800;
    margin-top: 10px;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 25px;
}

.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #ef233c);
    color: white;
    border-radius: 14px;
    height: 48px;
    font-weight: 700;
    border: none;
}

.stButton > button:hover {
    color: white;
    opacity: 0.92;
}
</style>
""", unsafe_allow_html=True)

st.image("Logo.png", use_container_width=True)

st.markdown("<div class='login-card'>", unsafe_allow_html=True)

st.markdown("<div class='title'>Iniciar sesión</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Accede al panel administrativo de CyberLey</div>", unsafe_allow_html=True)

email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión", use_container_width=True):
    if email == "" or password == "":
        st.warning("Por favor ingresa correo y contraseña.")
    else:
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.success("✅ Login exitoso")
            st.write(f"Bienvenido: {response.user.email}")

        except Exception as e:
            st.error("❌ Error al iniciar sesión")
            st.write(e)

st.write("")

if st.button("Crear cuenta nueva", use_container_width=True):
    st.switch_page("pages/registro.py")

st.markdown("</div>", unsafe_allow_html=True)