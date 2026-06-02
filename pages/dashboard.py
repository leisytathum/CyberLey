import streamlit as st

st.set_page_config(
    page_title="CyberLey | Admin",
    page_icon="🛡️",
    layout="wide"
)

# =========================
# CSS
# =========================
def cargar_css():
    with open("css/dashboard.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()

# =========================
# VALIDAR SESIÓN
# =========================
if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

# =========================
# SIDEBAR ADMIN
# =========================
with st.sidebar:
    st.image("Logo.png", use_container_width=True)

    st.markdown("<div class='sidebar-title'>Panel Admin</div>", unsafe_allow_html=True)

    menu = st.radio(
        "Menú",
        [
            "🏠 Inicio",
            "👥 Participantes",
            "📝 Encuestas",
            "⚠️ Riesgo",
            "📊 Dashboards",
            "📚 Guías",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        label_visibility="collapsed"
    )
    if menu == "👥 Participantes":
        st.switch_page("pages/participantes.py")
    elif menu == "📝 Encuestas":
        st.switch_page("pages/encuestas.py")

    st.divider()

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# =========================
# DASHBOARD ADMIN
# =========================

nombre_admin = st.session_state.get("nombre", "Administradora")

st.markdown(f"""
<div class="topbar">
<div class="menu-icon">☰</div>
<div class="admin-info">
<span class="bell">🔔</span>
<span class="admin-avatar">👤</span>
<div>
<b>{nombre_admin}</b><br>
<small>Rol: Administrador</small>
</div>
</div>
</div>

<div class="dashboard-header">
<div>
<h1>¡Bienvenida, {nombre_admin}! 👋</h1>
<p>Resumen general del sistema de análisis de hábitos digitales y ciberseguridad.</p>
</div>

<div class="header-actions">
<button>👤 Ver participantes</button>
<button class="green-btn">📋 Nueva encuesta</button>
<button class="purple-btn">📄 Generar reporte</button>
</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="metric-card blue">
        <div class="metric-icon">👥</div>
        <div>
            <p>Participantes registrados</p>
            <h2>256</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card green">
        <div class="metric-icon">📋</div>
        <div>
            <p>Encuestas realizadas</p>
            <h2>312</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card red">
        <div class="metric-icon">⚠️</div>
        <div>
            <p>Riesgo alto</p>
            <h2>28%</h2>
            <small>87 participantes</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card yellow">
        <div class="metric-icon">🛡️</div>
        <div>
            <p>Riesgo medio</p>
            <h2>46%</h2>
            <small>143 participantes</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="metric-card green">
        <div class="metric-icon">✅</div>
        <div>
            <p>Riesgo bajo</p>
            <h2>26%</h2>
            <small>82 participantes</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

col_a, col_b, col_c = st.columns([1.1, 1.1, 1])

with col_a:
    st.markdown("""
    <div class="admin-card">
        <h3>Distribución de nivel de riesgo</h3>
        <div class="fake-chart">
            <div class="donut">46%</div>
        </div>
        <p>🔴 Riesgo alto — 28%</p>
        <p>🟡 Riesgo medio — 46%</p>
        <p>🟢 Riesgo bajo — 26%</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="admin-card">
        <h3>Tendencia de riesgo</h3>
        <div class="line-placeholder">
            <p>📈 Gráfico de tendencia últimos 6 meses</p>
        </div>
        <p>🔴 Riesgo alto &nbsp;&nbsp; 🟡 Riesgo medio &nbsp;&nbsp; 🟢 Riesgo bajo</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="admin-card">
        <h3>Alertas importantes</h3>
        <div class="alert-box red-alert">⚠️ El 28% de los participantes tiene riesgo alto.</div>
        <div class="alert-box yellow-alert">🔐 El uso de la misma contraseña es frecuente.</div>
        <div class="alert-box blue-alert">ℹ️ Reforzar educación en phishing.</div>
    </div>
    """, unsafe_allow_html=True)
    