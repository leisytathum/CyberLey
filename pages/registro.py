import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

load_dotenv()

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="CyberLey | Registro",
    page_icon="📝",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #ffffff 0%, #f8f5ff 45%, #fff1f2 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 480px;
    padding-top: 50px;
}

.register-card {
    background: white;
    padding: 35px;
    border-radius: 24px;
    box-shadow: 0px 12px 35px rgba(239, 35, 60, 0.16);
    border: 1px solid #ffe4e6;
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
    background: linear-gradient(90deg, #ef233c, #7c3aed);
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

st.markdown("<div class='register-card'>", unsafe_allow_html=True)

st.markdown("<div class='title'>Crear cuenta</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Registra un usuario para probar el sistema</div>", unsafe_allow_html=True)

nuevo_email = st.text_input("Correo electrónico")
nueva_password = st.text_input("Contraseña", type="password")

if st.button("Crear cuenta", use_container_width=True):
    if nuevo_email == "" or nueva_password == "":
        st.warning("Completa todos los campos.")
    else:
        try:
            supabase.auth.sign_up({
                "email": nuevo_email,
                "password": nueva_password
            })

            st.success("✅ Usuario registrado correctamente.")
            st.info("Ahora puedes volver a Login e iniciar sesión.")

        except Exception as e:
            st.error("❌ Error al registrar usuario")
            st.write(e)

st.markdown("</div>", unsafe_allow_html=True)
st.write("")

if st.button("Volver a iniciar sesión", use_container_width=True):
    st.switch_page("app.py")