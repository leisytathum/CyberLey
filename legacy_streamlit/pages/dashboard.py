import os
from pathlib import Path
import html

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Panel Administrador",
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
# VALIDAR ACCESO ADMIN
# =========================

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

if st.session_state.get("rol") != "admin":
    st.warning("Esta sección es exclusiva para administradores.")
    st.switch_page("pages/usuario.py")


# =========================
# DATOS DEL ADMINISTRADOR
# =========================

try:
    perfil_admin_response = (
        supabase
        .table("perfiles")
        .select("nombre_completo")
        .eq(
            "id",
            st.session_state["usuario_id"]
        )
        .limit(1)
        .execute()
    )

    perfiles_admin = (
        perfil_admin_response.data
        or []
    )

    if perfiles_admin:
        nombre_admin = (
            perfiles_admin[0]
            .get("nombre_completo")
            or "Administrador"
        )

    else:
        nombre_admin = "Administrador"

except Exception:
    nombre_admin = st.session_state.get(
        "nombre",
        "Administrador"
    )


st.session_state["nombre"] = nombre_admin

nombre_admin_seguro = html.escape(
    str(nombre_admin)
)

partes_nombre = nombre_admin_seguro.split()

if len(partes_nombre) >= 2:
    iniciales_admin = (
        partes_nombre[0][0]
        + partes_nombre[1][0]
    ).upper()

elif len(partes_nombre) == 1:
    iniciales_admin = (
        partes_nombre[0][0]
    ).upper()

else:
    iniciales_admin = "A"


# =========================
# CARGAR CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "dashboard.css"

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
# CONSULTAR TABLAS
# =========================

def consultar_tabla(
    nombre_tabla: str,
    columnas: str = "*"
) -> list[dict]:

    respuesta = (
        supabase
        .table(nombre_tabla)
        .select(columnas)
        .execute()
    )

    return respuesta.data or []


try:
    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, id_usuario, nombre_completo, "
            "ciudad, nivel_educativo"
        )
    )

    perfiles = consultar_tabla(
        "perfiles",
        "id, rol"
    )

    respuestas_ciberseguridad = consultar_tabla(
        "respuestas_encuesta_ciberseguridad",
        (
            "id_respuesta, id_usuario, fecha_respuesta, usa_nube, "
            "plataforma_nube, contenido_nube, nivel_conocimiento, "
            "manejo_ciberseguridad, frecuencia_info_seguridad, "
            "reconoce_phishing, identifica_herramientas_seguridad, "
            "estado_antivirus, tipo_conexion, estabilidad_conexion, "
            "frecuencia_fallas_internet, cambio_contrasenas_anual, "
            "reutiliza_contrasenas, importancia_actualizar_contrasenas, "
            "puntaje_riesgo, clasificacion_riesgo, observacion"
        )
    )

except Exception as error:
    st.error("No se pudieron cargar los datos del dashboard.")
    st.write(error)
    st.stop()


# =========================
# EXCLUIR ADMINISTRADORES
# =========================

df_participantes = pd.DataFrame(
    participantes
)

df_perfiles = pd.DataFrame(
    perfiles
)

if (
    not df_participantes.empty
    and not df_perfiles.empty
):

    df_participantes = (
        df_participantes
        .merge(
            df_perfiles,
            left_on="id_usuario",
            right_on="id",
            how="left"
        )
    )

    df_participantes = (
        df_participantes[
            df_participantes["rol"] == "usuario"
        ]
        .copy()
    )

    participantes = (
        df_participantes
        .to_dict(
            orient="records"
        )
    )


# =========================
# PROCESAR MÉTRICAS
# =========================

total_participantes = len(participantes)
total_encuestas = len(respuestas_ciberseguridad)

df_resultados = pd.DataFrame(
    respuestas_ciberseguridad
)

if df_resultados.empty:
    cantidad_alto = 0
    cantidad_medio = 0
    cantidad_bajo = 0

else:
    cantidad_alto = len(
        df_resultados[
            df_resultados["clasificacion_riesgo"] == "alto"
        ]
    )

    cantidad_medio = len(
        df_resultados[
            df_resultados["clasificacion_riesgo"] == "medio"
        ]
    )

    cantidad_bajo = len(
        df_resultados[
            df_resultados["clasificacion_riesgo"] == "bajo"
        ]
    )


def calcular_porcentaje(
    cantidad: int,
    total: int
) -> float:

    if total == 0:
        return 0

    return round(
        cantidad / total * 100,
        1
    )


porcentaje_alto = calcular_porcentaje(
    cantidad_alto,
    total_encuestas
)

porcentaje_medio = calcular_porcentaje(
    cantidad_medio,
    total_encuestas
)

porcentaje_bajo = calcular_porcentaje(
    cantidad_bajo,
    total_encuestas
)


# =========================
# SIDEBAR ADMINISTRADOR
# =========================

with st.sidebar:

    st.image(
        str(ROOT_DIR / "Logo.png"),
        use_container_width=True
    )

    st.markdown(
        "<div class='sidebar-title'>Panel Administrador</div>",
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Menú",
        [
            "🏠 Inicio",
            "👥 Participantes",
            "📝 Encuestas",
            "⚠️ Riesgo",
            "🧹 Limpieza de datos",
            "📥 Importar datos históricos",
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "🚪 Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.clear()
        st.switch_page("app.py")


# =========================
# NAVEGACIÓN DEL SIDEBAR
# =========================

if menu == "👥 Participantes":
    st.switch_page("pages/participantes.py")

elif menu == "📝 Encuestas":
    st.switch_page("pages/encuestas.py")

elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")

elif menu == "📥 Importar datos históricos":
    st.switch_page("pages/importar_datos.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "📄 Reportes":
    st.switch_page("pages/reportes.py")

elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")


# =========================
# ENCABEZADO
# =========================

st.markdown(
    f"""
<div class="topbar">
<div class="topbar-left">
<span class="topbar-label">Panel administrativo</span>
</div>

<div class="topbar-right">
<div class="notification-wrapper">
<span class="notification-icon">🔔</span>
<span class="notification-dot"></span>
</div>

<div class="admin-avatar">{iniciales_admin}</div>

<div class="admin-profile-text">
<strong>{nombre_admin_seguro}</strong>
<small>Rol: Administrador</small>
</div>
</div>
</div>

<div class="dashboard-header">
<div class="welcome-content">
<span class="welcome-badge">Panel de control</span>

<h1>¡Bienvenida, {nombre_admin_seguro}! 👋</h1>

<p>
Consulta el resumen general de participantes,
evaluaciones y niveles de riesgo digital.
</p>
</div>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# TARJETAS DE MÉTRICAS
# =========================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
<div class="metric-card purple">
<div class="metric-icon">👥</div>
<div>
<p>Participantes</p>
<h2>{total_participantes}</h2>
<small>Registrados</small>
</div>
</div>
""",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card blue">
<div class="metric-icon">📝</div>
<div>
<p>Encuestas</p>
<h2>{total_encuestas}</h2>
<small>Completadas</small>
</div>
</div>
""",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card red">
<div class="metric-icon">⚠️</div>
<div>
<p>Riesgo alto</p>
<h2>{porcentaje_alto}%</h2>
<small>{cantidad_alto} resultados</small>
</div>
</div>
""",
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
<div class="metric-card yellow">
<div class="metric-icon">🛡️</div>
<div>
<p>Riesgo medio</p>
<h2>{porcentaje_medio}%</h2>
<small>{cantidad_medio} resultados</small>
</div>
</div>
""",
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
<div class="metric-card green">
<div class="metric-icon">✅</div>
<div>
<p>Riesgo bajo</p>
<h2>{porcentaje_bajo}%</h2>
<small>{cantidad_bajo} resultados</small>
</div>
</div>
""",
        unsafe_allow_html=True
    )


st.write("")


# =========================
# GRÁFICOS Y ALERTAS
# =========================

col_grafico, col_tendencia, col_alertas = st.columns(
    [1, 1.15, 1]
)


with col_grafico:

    st.markdown(
        """
        <div class="section-title">
            Distribución del nivel de riesgo
        </div>
        """,
        unsafe_allow_html=True
    )

    grafico_riesgo = pd.DataFrame({
        "Nivel de riesgo": [
            "Alto",
            "Medio",
            "Bajo"
        ],
        "Cantidad": [
            cantidad_alto,
            cantidad_medio,
            cantidad_bajo
        ]
    })

    if grafico_riesgo["Cantidad"].sum() == 0:
        st.info("Todavía no existen resultados de riesgo.")

    else:
        st.bar_chart(
            grafico_riesgo,
            x="Nivel de riesgo",
            y="Cantidad",
            use_container_width=True
        )


with col_tendencia:

    st.markdown(
        """
        <div class="section-title">
            Tendencia de evaluaciones
        </div>
        """,
        unsafe_allow_html=True
    )

    if not respuestas_ciberseguridad:
        st.info("Todavía no existen encuestas completadas.")

    else:
        df_encuestas = pd.DataFrame(
            respuestas_ciberseguridad
        )

        df_encuestas["fecha_respuesta"] = pd.to_datetime(
            df_encuestas["fecha_respuesta"],
            errors="coerce"
        )

        tendencia = (
            df_encuestas
            .dropna(
                subset=["fecha_respuesta"]
            )
            .assign(
                fecha=lambda datos: (
                    datos["fecha_respuesta"]
                    .dt.date
                )
            )
            .groupby("fecha")
            .size()
            .reset_index(
                name="Encuestas"
            )
        )

        st.line_chart(
            tendencia,
            x="fecha",
            y="Encuestas",
            use_container_width=True
        )


with col_alertas:

    st.markdown(
        """
        <div class="section-title">
            Alertas importantes
        </div>
        """,
        unsafe_allow_html=True
    )

    if not respuestas_ciberseguridad:
        st.info("Todavía no existen alertas.")

    else:
        if porcentaje_alto > 0:
            st.error(
                f"⚠️ {porcentaje_alto}% de los resultados "
                "presenta riesgo alto."
            )

        if porcentaje_medio > 0:
            st.warning(
                f"🛡️ {porcentaje_medio}% de los resultados "
                "presenta riesgo medio."
            )

        if porcentaje_bajo > 0:
            st.success(
                f"✅ {porcentaje_bajo}% de los resultados "
                "presenta riesgo bajo."
            )


# =========================
# HÁBITOS INSEGUROS
# =========================

st.write("")

st.markdown(
    """
    <div class="section-title">
        Hábitos inseguros más frecuentes
    </div>
    """,
    unsafe_allow_html=True
)

if not respuestas_ciberseguridad:
    st.info("Todavía no existen respuestas para analizar.")

else:
    df_respuestas = pd.DataFrame(
        respuestas_ciberseguridad
    )

    habitos = {
        "Reutiliza contraseñas": int(
            df_respuestas[
                df_respuestas["reutiliza_contrasenas"].isin(
                    [
                        "Sí",
                        "A veces"
                    ]
                )
            ].shape[0]
        ),

        "No reconoce phishing": int(
            df_respuestas[
                df_respuestas["reconoce_phishing"].isin(
                    [
                        "No",
                        "A veces"
                    ]
                )
            ].shape[0]
        ),

        "Antivirus desactualizado o ausente": int(
            df_respuestas[
                df_respuestas["estado_antivirus"].isin(
                    [
                        "No tengo antivirus",
                        "Tengo antivirus, pero no está actualizado",
                        "No sé"
                    ]
                )
            ].shape[0]
        ),

        "Bajo conocimiento": int(
            df_respuestas[
                df_respuestas["nivel_conocimiento"] == "Bajo"
            ].shape[0]
        ),

        "Nunca cambia contraseñas": int(
            df_respuestas[
                df_respuestas["cambio_contrasenas_anual"] == "Nunca"
            ].shape[0]
        ),

        "Poca información de seguridad": int(
            df_respuestas[
                df_respuestas["frecuencia_info_seguridad"].isin(
                    [
                        "Nunca",
                        "Rara vez"
                    ]
                )
            ].shape[0]
        )
    }

    df_habitos = (
        pd.DataFrame(
            list(habitos.items()),
            columns=[
                "Hábito inseguro",
                "Cantidad"
            ]
        )
        .sort_values(
            "Cantidad",
            ascending=False
        )
    )

    st.bar_chart(
        df_habitos,
        x="Hábito inseguro",
        y="Cantidad",
        use_container_width=True
    )


# =========================
# TABLA DE ÚLTIMAS EVALUACIONES
# =========================

st.write("")

st.markdown(
    """
    <div class="section-title">
        Últimas evaluaciones registradas
    </div>
    """,
    unsafe_allow_html=True
)

if not respuestas_ciberseguridad:
    st.info("Todavía no existen evaluaciones registradas.")

else:
    df_ultimas = pd.DataFrame(
        respuestas_ciberseguridad
    )

    df_ultimas["fecha_respuesta"] = pd.to_datetime(
        df_ultimas["fecha_respuesta"],
        errors="coerce"
    )

    columnas_mostrar = [
        "fecha_respuesta",
        "nivel_conocimiento",
        "reconoce_phishing",
        "estado_antivirus",
        "reutiliza_contrasenas",
        "puntaje_riesgo",
        "clasificacion_riesgo"
    ]

    df_ultimas = (
        df_ultimas[columnas_mostrar]
        .sort_values(
            "fecha_respuesta",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        df_ultimas,
        use_container_width=True,
        hide_index=True
    )