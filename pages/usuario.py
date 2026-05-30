import streamlit as st

st.set_page_config(
    page_title="CyberLey | Usuario",
    page_icon="🛡️",
    layout="wide"
)

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

nombre = st.session_state.get("nombre", "Usuario")

st.title(f"¡Hola, {nombre}! 👋")

st.info(
    "Tu panel de usuario se encuentra en construcción. "
    "Próximamente podrás completar encuestas, consultar tu nivel "
    "de riesgo y revisar guías de ciberseguridad."
)

if st.button("Cerrar sesión"):
    st.session_state.clear()
    st.switch_page("app.py")