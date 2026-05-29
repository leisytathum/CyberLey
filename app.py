import os
from dotenv import load_dotenv
from supabase import create_client, Client

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

st.markdown("""
    <h1 style='text-align:center; color:#2563eb;'>CyberLey</h1>
    <p style='text-align:center;'>Sistema de análisis de hábitos digitales y ciberseguridad</p>
""", unsafe_allow_html=True)

st.divider()

# =========================
# FORMULARIO LOGIN
# =========================

st.subheader("Iniciar sesión")

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